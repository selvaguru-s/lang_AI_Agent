#!/usr/bin/env python3
"""
AI Linux Agent Client

This is the main client that connects to the backend server and executes
commands remotely while sending detailed execution logs to the frontend.
"""

import asyncio
import json
import logging
import os
import subprocess
import websockets
from datetime import datetime
import uuid
import platform
import socket
from typing import Optional, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class ClientLogger:
    """Client logger that sends detailed execution logs to backend via WebSocket"""
    
    def __init__(self, websocket, machine_id: str):
        self.websocket = websocket
        self.machine_id = machine_id
        self.logger = logging.getLogger('client')
        
    async def log_info(self, message: str, task_id: str = "system", context: dict = None):
        """Log info level message"""
        await self._send_log("info", message, task_id, context)
    
    async def log_debug(self, message: str, task_id: str = "system", context: dict = None):
        """Log debug level message"""
        await self._send_log("debug", message, task_id, context)
    
    async def log_warning(self, message: str, task_id: str = "system", context: dict = None):
        """Log warning level message"""
        await self._send_log("warning", message, task_id, context)
    
    async def log_error(self, message: str, task_id: str = "system", context: dict = None):
        """Log error level message"""
        await self._send_log("error", message, task_id, context)
    
    async def log_command_execution(self, task_id: str, subtask_id: str, command: str, attempt: int = 1):
        """Log command execution start"""
        await self.log_info(
            f"Executing command for task {task_id}, subtask {subtask_id}, attempt {attempt}: {command}",
            task_id=task_id,
            context={
                "subtask_id": subtask_id,
                "command": command,
                "attempt": attempt,
                "action": "command_start"
            }
        )
    
    async def log_command_completion(self, task_id: str, command: str, exit_code: int, execution_time: float = None):
        """Log command completion"""
        message = f"Command completed with exit code {exit_code}"
        if execution_time:
            message += f" (execution time: {execution_time:.2f}s)"
        
        await self.log_info(
            message,
            task_id=task_id,
            context={
                "command": command,
                "exit_code": exit_code,
                "execution_time": execution_time,
                "action": "command_complete"
            }
        )
    
    async def _send_log(self, level: str, message: str, task_id: str = "system", context: dict = None):
        """Send log message to backend via WebSocket"""
        try:
            log_message = {
                "type": "client_log",
                "task_id": task_id,
                "level": level,
                "message": message,
                "logger": "client",
                "context": context or {},
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
            
            # Send to backend
            await self.websocket.send(json.dumps(log_message))
            
            # Also log locally
            log_method = getattr(self.logger, level.lower(), self.logger.info)
            log_method(message, extra={"context": context})
            
        except Exception as e:
            # Fallback to local logging if WebSocket fails
            self.logger.error(f"Failed to send log to backend: {e}")
            log_method = getattr(self.logger, level.lower(), self.logger.info)
            log_method(message, extra={"context": context})


class AILinuxClient:
    """AI Linux Agent Client"""
    
    def __init__(self):
        self.api_key = os.getenv("API_KEY")
        self.server_url = os.getenv("SERVER_URL", "ws://localhost:8000")
        self.heartbeat_interval = int(os.getenv("HEARTBEAT_INTERVAL", "30"))
        self.machine_id = self._get_or_create_machine_id()
        self.websocket = None
        self.client_logger = None
        self.running = False
        
        # Configure logging level
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        logging.getLogger().setLevel(getattr(logging, log_level))
    
    def _get_mac_address(self) -> str:
        """Get the MAC address of the primary network interface"""
        import subprocess
        try:
            # Get MAC address from primary interface
            result = subprocess.run(['ip', 'link', 'show'], 
                                  capture_output=True, text=True, check=True)
            
            # Extract MAC address from output
            for line in result.stdout.split('\n'):
                if 'link/ether' in line and 'ether' in line:
                    parts = line.strip().split()
                    for i, part in enumerate(parts):
                        if part == 'link/ether' and i + 1 < len(parts):
                            return parts[i + 1]
            
            # Fallback: try using uuid.getnode()
            import uuid
            mac = uuid.getnode()
            mac_hex = f"{mac:012x}"
            return ":".join(mac_hex[i:i+2] for i in range(0, 12, 2))
            
        except Exception as e:
            print(f"Warning: Could not get MAC address: {e}")
            # Ultimate fallback
            import uuid
            mac = uuid.getnode()
            mac_hex = f"{mac:012x}"
            return ":".join(mac_hex[i:i+2] for i in range(0, 12, 2))
    
    def _get_or_create_machine_id(self) -> str:
        """Get or create unique machine ID using same algorithm as backend"""
        machine_id_file = os.path.join(os.path.dirname(__file__), "config", "machine_id")
        
        try:
            # Try to load existing machine ID
            with open(machine_id_file, 'r') as f:
                machine_id = f.read().strip()
                if machine_id:
                    return machine_id
        except FileNotFoundError:
            pass
        
        # Create new machine ID using same algorithm as backend
        hostname = socket.gethostname()
        mac_address = self._get_mac_address()
        
        # Generate unique 8-character hash using same method as backend
        import hashlib
        system_info = f"{hostname}_{mac_address}_salt_2024"
        hash_obj = hashlib.sha256(system_info.encode())
        unique_hash = hash_obj.hexdigest()[:8]
        
        # Format: {mac_without_colons}_{hostname}_{unique_hash}
        clean_mac = mac_address.replace(":", "")
        machine_id = f"{clean_mac}_{hostname}_{unique_hash}"
        
        # Save machine ID
        os.makedirs(os.path.dirname(machine_id_file), exist_ok=True)
        with open(machine_id_file, 'w') as f:
            f.write(machine_id)
            
        return machine_id
    
    async def run(self):
        """Main client loop"""
        self.running = True
        
        while self.running:
            try:
                await self._connect_and_run()
            except KeyboardInterrupt:
                print("Client interrupted by user")
                break
            except Exception as e:
                print(f"Connection failed: {e}")
                print("Retrying in 10 seconds...")
                await asyncio.sleep(10)
        
        self.running = False
    
    async def _connect_and_run(self):
        """Connect to server and handle messages"""
        # Build WebSocket URL
        ws_url = self.server_url.replace("http://", "ws://").replace("https://", "wss://")
        if not ws_url.startswith(("ws://", "wss://")):
            ws_url = f"ws://{ws_url}"
        
        uri = f"{ws_url}/ws/client?api_key={self.api_key}&machine_id={self.machine_id}"
        
        print(f"Connecting to {uri}")
        
        async with websockets.connect(uri) as websocket:
            self.websocket = websocket
            self.client_logger = ClientLogger(websocket, self.machine_id)
            
            # Log startup
            await self.client_logger.log_info(
                f"Loaded existing machine ID: {self.machine_id}",
                context={"machine_id": self.machine_id, "action": "machine_startup"}
            )
            
            await self.client_logger.log_info(
                "Starting AI Linux Client...",
                context={"action": "client_startup"}
            )
            
            await self.client_logger.log_info(
                f"Connected to server: {self.server_url}",
                context={"action": "connection_established", "server_url": self.server_url}
            )
            
            # Send system info
            await self._send_system_info()
            
            # Start heartbeat task
            heartbeat_task = asyncio.create_task(self._heartbeat_loop())
            
            try:
                # Handle incoming messages
                async for message in websocket:
                    await self._handle_message(json.loads(message))
                    
            finally:
                heartbeat_task.cancel()
                try:
                    await heartbeat_task
                except asyncio.CancelledError:
                    pass
    
    async def _send_system_info(self):
        """Send system information to server"""
        system_info = {
            "os": platform.system(),
            "arch": platform.machine(),
            "hostname": socket.gethostname(),
            "python_version": platform.python_version()
        }
        
        message = {
            "type": "system_info_update",
            "system_info": system_info
        }
        
        await self.websocket.send(json.dumps(message))
        
        await self.client_logger.log_debug(
            f"System info sent: {system_info}",
            context={"action": "system_info_sent", "system_info": system_info}
        )
    
    async def _heartbeat_loop(self):
        """Send periodic heartbeat messages"""
        while self.running:
            try:
                await asyncio.sleep(self.heartbeat_interval)
                
                if self.websocket:
                    heartbeat_message = {
                        "type": "heartbeat",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    
                    await self.websocket.send(json.dumps(heartbeat_message))
                    
                    if self.client_logger:
                        await self.client_logger.log_debug(
                            "Heartbeat sent",
                            context={"action": "heartbeat"}
                        )
                        
            except asyncio.CancelledError:
                break
            except Exception as e:
                if self.client_logger:
                    await self.client_logger.log_error(
                        f"Heartbeat failed: {e}",
                        context={"action": "heartbeat_error", "error": str(e)}
                    )
    
    async def _handle_message(self, message: Dict[str, Any]):
        """Handle incoming messages from server"""
        message_type = message.get("type")
        
        if message_type == "execute_command":
            await self._execute_command(message)
        elif message_type == "user_input":
            await self._handle_user_input(message)
        else:
            if self.client_logger:
                await self.client_logger.log_debug(
                    f"Received unknown message type: {message_type}",
                    context={"message_type": message_type, "message": message}
                )
    
    async def _execute_command(self, message: Dict[str, Any]):
        """Execute a command and send results back"""
        task_id = message.get("task_id")
        subtask_id = message.get("subtask_id")
        command = message.get("command")
        attempt_number = message.get("attempt_number", 1)
        
        if not all([task_id, subtask_id, command]):
            await self.client_logger.log_error(
                "Invalid execute_command message - missing required fields",
                task_id=task_id,
                context={"message": message}
            )
            return
        
        # Log command execution start
        await self.client_logger.log_command_execution(
            task_id, subtask_id, command, attempt_number
        )
        
        start_time = datetime.utcnow()
        
        try:
            # Execute command
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            exit_code = process.returncode
            
            # Decode bytes to text
            stdout_text = stdout.decode('utf-8', errors='replace') if stdout else ""
            stderr_text = stderr.decode('utf-8', errors='replace') if stderr else ""
            
            # Calculate execution time
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Log command completion
            await self.client_logger.log_command_completion(
                task_id, command, exit_code, execution_time
            )
            
            # Send result back to server
            result_message = {
                "type": "command_result",
                "task_id": task_id,
                "subtask_id": subtask_id,
                "command": command,
                "output": stdout_text + stderr_text,  # Combine stdout and stderr
                "exit_code": exit_code,
                "attempt_number": attempt_number,
                "execution_time": execution_time
            }
            
            await self.websocket.send(json.dumps(result_message))
            
            # Log if command failed
            if exit_code != 0:
                await self.client_logger.log_warning(
                    f"Command failed with exit code {exit_code}: {command}",
                    task_id=task_id,
                    context={
                        "command": command,
                        "exit_code": exit_code,
                        "stderr": stderr_text,
                        "action": "command_failed"
                    }
                )
            
        except Exception as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            await self.client_logger.log_error(
                f"Command execution error: {e}",
                task_id=task_id,
                context={
                    "command": command,
                    "error": str(e),
                    "action": "command_exception"
                }
            )
            
            # Send error result
            result_message = {
                "type": "command_result",
                "task_id": task_id,
                "subtask_id": subtask_id,
                "command": command,
                "output": f"Error executing command: {e}",
                "exit_code": -1,
                "attempt_number": attempt_number,
                "execution_time": execution_time
            }
            
            await self.websocket.send(json.dumps(result_message))
    
    async def _handle_user_input(self, message: Dict[str, Any]):
        """Handle user input for interactive commands"""
        user_input = message.get("input", "")
        
        await self.client_logger.log_info(
            f"Received user input: {user_input}",
            task_id=message.get("task_id", "system"),
            context={"action": "user_input_received", "input": user_input}
        )
        
        # TODO: Forward input to running interactive process
        # This would require more complex process management
    
    def stop(self):
        """Stop the client"""
        self.running = False