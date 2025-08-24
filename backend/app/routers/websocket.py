import json
import asyncio
from typing import Dict, Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from fastapi.websockets import WebSocketState
from utils.auth import verify_api_key
from utils.log_broadcaster import log_broadcaster
from config.database import get_database
from datetime import datetime
import re


router = APIRouter()


class ConnectionManager:
    def __init__(self):
        # Store active connections by type and identifier
        self.client_connections: Dict[str, WebSocket] = {}  # machine_id -> websocket
        self.user_connections: Dict[str, Set[WebSocket]] = {}  # user_id -> set of websockets
        
    async def connect_client(self, websocket: WebSocket, machine_id: str):
        """Connect a client machine"""
        await websocket.accept()
        self.client_connections[machine_id] = websocket
        print(f"Client {machine_id} connected")
        
    async def connect_user(self, websocket: WebSocket, user_id: str):
        """Connect a user dashboard"""
        await websocket.accept()
        if user_id not in self.user_connections:
            self.user_connections[user_id] = set()
        self.user_connections[user_id].add(websocket)
        print(f"User {user_id} dashboard connected")
        
    def disconnect_client(self, machine_id: str):
        """Disconnect a client machine"""
        if machine_id in self.client_connections:
            del self.client_connections[machine_id]
            print(f"Client {machine_id} disconnected")
            
    def disconnect_user(self, websocket: WebSocket, user_id: str):
        """Disconnect a user dashboard"""
        if user_id in self.user_connections:
            self.user_connections[user_id].discard(websocket)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
        print(f"User {user_id} dashboard disconnected")
        
    async def send_to_client(self, machine_id: str, message: dict):
        """Send message to specific client"""
        if machine_id in self.client_connections:
            websocket = self.client_connections[machine_id]
            if websocket.client_state == WebSocketState.CONNECTED:
                try:
                    await websocket.send_text(json.dumps(message))
                    return True
                except Exception as e:
                    print(f"Error sending to client {machine_id}: {e}")
                    self.disconnect_client(machine_id)
        return False
        
    async def send_to_user(self, user_id: str, message: dict):
        """Send message to all user dashboard connections"""
        print(f"📤 Attempting to send message to user {user_id}")
        print(f"📋 Available user connections: {list(self.user_connections.keys())}")
        print(f"📨 Message: {message}")
        
        if user_id in self.user_connections and len(self.user_connections[user_id]) > 0:
            print(f"✅ Found user {user_id} with {len(self.user_connections[user_id])} connections")
            disconnected = []
            sent_count = 0
            
            for websocket in self.user_connections[user_id].copy():
                if websocket.client_state == WebSocketState.CONNECTED:
                    try:
                        await websocket.send_text(json.dumps(message))
                        sent_count += 1
                        print(f"📧 Message sent successfully to user {user_id} connection {sent_count}")
                    except Exception as e:
                        print(f"❌ Error sending to user {user_id}: {e}")
                        disconnected.append(websocket)
                else:
                    print(f"⚠️ Websocket for user {user_id} not connected")
                    disconnected.append(websocket)
            
            print(f"📊 Sent message to {sent_count} connections for user {user_id}")
            
            # Clean up disconnected websockets
            for ws in disconnected:
                self.user_connections[user_id].discard(ws)
        else:
            print(f"❌ User {user_id} not found in user connections")


manager = ConnectionManager()


def is_executable_command(command_text: str) -> bool:
    """Check if the given text is an executable command rather than instructions"""
    if not command_text or not isinstance(command_text, str):
        return False
    
    # Remove leading/trailing whitespace
    cmd = command_text.strip()
    
    # Check for instruction phrases that indicate this is not a command
    instruction_phrases = [
        'run this',
        'try running', 
        'execute this',
        'start the',
        'in a separate',
        'in the background',
        'then run',
        'first run',
        'make sure',
        'please run',
        'you should',
        'to do this',
        'need to',
        'should be',
        'might need'
    ]
    
    cmd_lower = cmd.lower()
    for phrase in instruction_phrases:
        if phrase in cmd_lower:
            return False
    
    # Check if it looks like a command (starts with a command name, has proper syntax)
    # Should start with a word (command name) followed by space or end
    if not re.match(r'^[a-zA-Z0-9_/.-]+(\s|$)', cmd):
        return False
    
    # Should not be overly long (commands are typically concise)
    if len(cmd) > 200:
        return False
    
    # Should not contain multiple sentences
    if '. ' in cmd and not cmd.endswith('.'):
        return False
    
    return True


@router.websocket("/client")
async def websocket_client_endpoint(
    websocket: WebSocket,
    api_key: str = Query(...),
    machine_id: str = Query(...)
):
    """WebSocket endpoint for client machines"""
    
    # Verify API key
    user = await verify_api_key(api_key)
    if not user:
        await websocket.close(code=4001, reason="Invalid API key")
        return
        
    # Auto-register machine on first connection or verify existing machine
    db = await get_database()
    machine = await db.client_machines.find_one({"machine_id": machine_id})
    
    print(f"WebSocket auth - User: {user.email}, Machine ID: {machine_id}")
    print(f"WebSocket auth - User client_machines: {user.client_machines}")
    print(f"WebSocket auth - Machine exists: {machine is not None}")
    print(f"WebSocket auth - Machine in user list: {machine_id in user.client_machines}")
    
    # Auto-registration logic: If machine doesn't exist OR not in user's list, register it
    if not machine or machine_id not in user.client_machines:
        print(f"WebSocket auth - Auto-registering machine {machine_id} for user {user.email}")
        
        try:
            # Parse machine_id to extract system info (format: mac_hostname_hash)
            parts = machine_id.split('_')
            if len(parts) >= 2:
                hostname = parts[1] if len(parts) > 1 else "unknown"
                # Default values for auto-registration
                default_machine_data = {
                    "machine_id": machine_id,
                    "hostname": hostname,
                    "os_info": "Linux",  # Default, will be updated via system_info_update
                    "architecture": "x86_64",  # Default, will be updated via system_info_update
                    "mac_address": ":".join(parts[0][i:i+2] for i in range(0, min(len(parts[0]), 12), 2)),
                    "last_seen": datetime.utcnow(),
                    "is_active": True
                }
                
                # Create or update machine record
                await db.client_machines.update_one(
                    {"machine_id": machine_id},
                    {"$set": default_machine_data},
                    upsert=True
                )
                
                # Add machine to user's client_machines list if not already there
                if machine_id not in user.client_machines:
                    await db.users.update_one(
                        {"api_key": user.api_key},
                        {"$push": {"client_machines": machine_id}}
                    )
                    print(f"WebSocket auth - Added machine {machine_id} to user {user.email}")
                
                print(f"WebSocket auth - Auto-registration completed for {machine_id}")
                
            else:
                print(f"WebSocket auth - Invalid machine_id format: {machine_id}")
                await websocket.close(code=4002, reason="Invalid machine ID format")
                return
                
        except Exception as e:
            print(f"WebSocket auth - Auto-registration failed: {e}")
            await websocket.close(code=4002, reason="Machine registration failed")
            return
    
    # At this point, machine should exist and be authorized
    # Update machine status to active (in case it was set to inactive)
    await db.client_machines.update_one(
        {"machine_id": machine_id},
        {"$set": {"is_active": True, "last_seen": datetime.utcnow()}}
    )
    
    await manager.connect_client(websocket, machine_id)
    
    # Connect to log broadcaster
    client_log_id = f"client_{machine_id}"
    # Note: We'll get task_id from messages, not at connection time for clients
    
    # Update machine last_seen
    await db.client_machines.update_one(
        {"machine_id": machine_id},
        {"$set": {"last_seen": datetime.utcnow(), "is_active": True}}
    )
    
    # Log client connection
    await log_broadcaster.log_websocket_event(
        task_id="system",
        event_type="client_connected",
        message=f"Client {machine_id} connected",
        client_info={
            "machine_id": machine_id,
            "user_email": user.email
        }
    )
    
    try:
        while True:
            # Receive messages from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message.get("type") == "command_result":
                await handle_command_result(message, user.firebase_uid, machine_id)
            elif message.get("type") == "live_output":
                await handle_live_output(message, user.firebase_uid, machine_id)
            elif message.get("type") == "heartbeat":
                await handle_client_heartbeat(machine_id)
            elif message.get("type") == "system_info_update":
                await handle_system_info_update(message, machine_id)
            elif message.get("type") == "interactive_prompt":
                await handle_interactive_prompt(message, user.firebase_uid, machine_id)
            elif message.get("type") == "waiting_for_input":
                await handle_waiting_for_input(message, user.firebase_uid, machine_id)
            elif message.get("type") == "process_health_update":
                await handle_process_health_update(message, user.firebase_uid, machine_id)
            elif message.get("type") == "alternative_command_triggered":
                await handle_alternative_command_triggered(message, user.firebase_uid, machine_id)
            elif message.get("type") == "alternative_command_result":
                await handle_alternative_command_result(message, user.firebase_uid, machine_id)
            elif message.get("type") == "ai_summary_update":
                await handle_ai_summary_update(message, user.firebase_uid, machine_id)
            elif message.get("type") == "client_log":
                await handle_client_log(message, user.firebase_uid, machine_id)
                
    except WebSocketDisconnect:
        manager.disconnect_client(machine_id)
        # Mark machine as inactive
        await db.client_machines.update_one(
            {"machine_id": machine_id},
            {"$set": {"is_active": False}}
        )


@router.websocket("/dashboard")
async def websocket_dashboard_endpoint(
    websocket: WebSocket,
    api_key: str = Query(...)
):
    """WebSocket endpoint for user dashboard"""
    
    # Verify API key
    user = await verify_api_key(api_key)
    if not user:
        await websocket.close(code=4001, reason="Invalid API key")
        return
    
    user_id = user.firebase_uid  # Use Firebase UID as user ID
    print(f"Dashboard connecting - User: {user.email}, Firebase UID: {user_id}")
    await manager.connect_user(websocket, user_id)
    
    # Connect to log broadcaster for dashboard user
    dashboard_log_id = f"dashboard_{user_id}"
    # Task-specific log subscription will be handled via messages
    
    try:
        while True:
            # Keep connection alive and handle any dashboard-specific messages
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
            elif message.get("type") == "user_input":
                await handle_user_input(message, user_id)
            elif message.get("type") == "subscribe_to_logs":
                # Subscribe to logs for specific task
                task_id = message.get("task_id")
                if task_id:
                    await log_broadcaster.connect_client(dashboard_log_id, websocket, task_id)
                
    except WebSocketDisconnect:
        manager.disconnect_user(websocket, user_id)


async def handle_command_result(message: dict, user_id: str, machine_id: str):
    """Handle command execution result from client"""
    try:
        from utils.llm_service import llm_service
        
        db = await get_database()
        task_id = message.get("task_id")
        subtask_id = message.get("subtask_id")
        command = message.get("command")
        output = message.get("output", "")
        exit_code = message.get("exit_code", 0)
        attempt_number = message.get("attempt_number", 1)
        
        # Get task details
        task = await db.task_executions.find_one({"task_id": task_id})
        if not task:
            return
            
        # Find the subtask
        subtask = None
        for st in task["subtasks"]:
            if st["id"] == subtask_id:
                subtask = st
                break
                
        if not subtask:
            return
            
        # Log command execution
        await log_broadcaster.log_server_event(
            task_id=task_id,
            level="info",
            message=f"Command result received: {command}",
            details={
                "exit_code": exit_code,
                "output_length": len(output),
                "attempt_number": attempt_number
            },
            context={
                "machine_id": machine_id,
                "subtask_id": subtask_id
            }
        )
        
        # Validate output using LLM
        validation_result = await llm_service.validate_output(
            command, output, exit_code, subtask.get("expected_output", "")
        )
        
        # Log validation result
        await log_broadcaster.log_server_event(
            task_id=task_id,
            level="info" if validation_result.is_valid else "warning",
            message=f"Command validation: {'passed' if validation_result.is_valid else 'failed'}",
            details={
                "validation_result": validation_result.dict(),
                "command": command
            },
            context={
                "service": "llm_validator",
                "subtask_id": subtask_id
            }
        )
        
        # Create attempt record
        attempt = {
            "attempt_number": attempt_number,
            "command": command,
            "output": output,
            "exit_code": exit_code,
            "validation_result": validation_result.dict(),
            "timestamp": datetime.utcnow()
        }
        
        # Update task with attempt results
        set_update = {
            "status": "running"
        }
        
        if validation_result.is_valid:
            # Mark current subtask as completed
            set_update[f"subtasks.$.status"] = "completed"
            
            # Move to next subtask
            current_index = task["current_subtask_index"]
            if current_index + 1 >= len(task["subtasks"]):
                # Task completed
                set_update["status"] = "completed"
                set_update["completed_at"] = datetime.utcnow()
            else:
                set_update["current_subtask_index"] = current_index + 1
                
        elif attempt_number >= 3:
            # Max attempts reached, mark as failed
            set_update["status"] = "failed"
            set_update["error_message"] = validation_result.error_message
            set_update["completed_at"] = datetime.utcnow()
        
        # Update database - push attempt to the subtask's attempts array
        await db.task_executions.update_one(
            {"task_id": task_id, "subtasks.id": subtask_id},
            {
                "$set": set_update,
                "$push": {"subtasks.$.attempts": attempt}
            }
        )
        
        # If task completed, generate AI summary with updated data
        if validation_result.is_valid and current_index + 1 >= len(task["subtasks"]):
            try:
                # Get updated task data with all attempts
                updated_task = await db.task_executions.find_one({"task_id": task_id})
                if updated_task:
                    system_info = {
                        "os": "Linux", 
                        "arch": "x86_64"
                    }
                    ai_summary = await llm_service.generate_task_summary(
                        updated_task["original_prompt"], 
                        updated_task["subtasks"], 
                        system_info
                    )
                    # Update with AI summary
                    await db.task_executions.update_one(
                        {"task_id": task_id},
                        {"$set": {"ai_summary": ai_summary}}
                    )
            except Exception as e:
                print(f"Error generating AI summary: {e}")
                await db.task_executions.update_one(
                    {"task_id": task_id},
                    {"$set": {"ai_summary": "Task completed successfully."}}
                )
        
        # Send update to user dashboard
        dashboard_message = {
            "type": "task_update",
            "task_id": task_id,
            "subtask_id": subtask_id,
            "status": set_update["status"],
            "attempt": attempt,
            "validation": validation_result.dict()
        }
        
        print(f"🚀 Sending task_update to user {user_id}: {dashboard_message}")
        await manager.send_to_user(user_id, dashboard_message)
        print(f"✅ Sent task_update to user {user_id}")
        
        # If task needs to continue, send next command to client
        if validation_result.is_valid and set_update.get("current_subtask_index") is not None:
            next_index = set_update["current_subtask_index"]
            if next_index < len(task["subtasks"]):
                next_subtask = task["subtasks"][next_index]
                client_message = {
                    "type": "execute_command",
                    "task_id": task_id,
                    "subtask_id": next_subtask["id"],
                    "command": next_subtask["command"],
                    "attempt_number": 1
                }
                await manager.send_to_client(machine_id, client_message)
        elif not validation_result.is_valid and validation_result.should_retry and attempt_number < 3:
            # Retry with suggested fix or original command
            suggested_fix = validation_result.suggested_fix or command
            
            # Validate that suggested fix is an actual command, not instructions
            if suggested_fix and not is_executable_command(suggested_fix):
                print(f"❌ Invalid suggested fix (not executable): {suggested_fix}")
                suggested_fix = command  # Fall back to original command
            
            client_message = {
                "type": "execute_command",
                "task_id": task_id,
                "subtask_id": subtask_id,
                "command": suggested_fix,
                "attempt_number": attempt_number + 1
            }
            await manager.send_to_client(machine_id, client_message)
            
    except Exception as e:
        print(f"Error handling command result: {e}")


async def handle_client_heartbeat(machine_id: str):
    """Handle client heartbeat"""
    db = await get_database()
    await db.client_machines.update_one(
        {"machine_id": machine_id},
        {"$set": {"last_seen": datetime.utcnow()}}
    )


async def handle_live_output(message: dict, user_id: str, machine_id: str):
    """Handle live output streaming from client"""
    try:
        # Forward live output to user dashboard
        dashboard_message = {
            "type": "live_output",
            "task_id": message.get("task_id"),
            "subtask_id": message.get("subtask_id"),
            "attempt_number": message.get("attempt_number"),
            "stream": message.get("stream"),  # 'stdout' or 'stderr'
            "data": message.get("data"),
            "machine_id": machine_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await manager.send_to_user(user_id, dashboard_message)
        
    except Exception as e:
        print(f"Error handling live output: {e}")


async def handle_system_info_update(message: dict, machine_id: str):
    """Handle system information update from client"""
    db = await get_database()
    system_info = message.get("system_info", {})
    
    await db.client_machines.update_one(
        {"machine_id": machine_id},
        {"$set": {
            "os_info": system_info.get("os", ""),
            "architecture": system_info.get("arch", ""),
            "hostname": system_info.get("hostname", ""),
            "last_seen": datetime.utcnow()
        }}
    )


# Function to start a task execution
async def start_task_execution(task_id: str, user_id: str, machine_id: str):
    """Start executing a task by sending first command to client"""
    try:
        db = await get_database()
        task = await db.task_executions.find_one({"task_id": task_id})
        
        if not task or not task["subtasks"]:
            return False
            
        # Send first subtask to client
        first_subtask = task["subtasks"][0]
        client_message = {
            "type": "execute_command",
            "task_id": task_id,
            "subtask_id": first_subtask["id"],
            "command": first_subtask["command"],
            "attempt_number": 1
        }
        
        # Update task status to running
        await db.task_executions.update_one(
            {"task_id": task_id},
            {"$set": {"status": "running"}}
        )
        
        success = await manager.send_to_client(machine_id, client_message)
        
        # Notify user dashboard
        dashboard_message = {
            "type": "task_started",
            "task_id": task_id,
            "machine_id": machine_id
        }
        await manager.send_to_user(user_id, dashboard_message)
        
        return success
        
    except Exception as e:
        print(f"Error starting task execution: {e}")
        return False


async def handle_user_input(message: dict, user_id: str):
    """Handle user input from dashboard to be sent to interactive process"""
    try:
        task_id = message.get("task_id")
        user_input = message.get("input", "")
        machine_id = message.get("machine_id")
        
        if not all([task_id, machine_id]):
            print(f"Missing required fields in user input: task_id={task_id}, machine_id={machine_id}")
            return
            
        # Send user input to the appropriate client
        client_message = {
            "type": "user_input",
            "task_id": task_id,
            "input": user_input
        }
        
        success = await manager.send_to_client(machine_id, client_message)
        print(f"Sent user input to client {machine_id}: {user_input} (success: {success})")
        
    except Exception as e:
        print(f"Error handling user input: {e}")


async def handle_interactive_prompt(message: dict, user_id: str, machine_id: str):
    """Handle interactive prompt notification from client"""
    try:
        # Forward interactive prompt to user dashboard
        dashboard_message = {
            "type": "interactive_prompt",
            "task_id": message.get("task_id"),
            "data": message.get("data"),
            "machine_id": machine_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await manager.send_to_user(user_id, dashboard_message)
        print(f"Forwarded interactive prompt to user {user_id}")
        
    except Exception as e:
        print(f"Error handling interactive prompt: {e}")


async def handle_waiting_for_input(message: dict, user_id: str, machine_id: str):
    """Handle waiting for input notification from client"""
    try:
        # Forward waiting notification to user dashboard
        dashboard_message = {
            "type": "waiting_for_input",
            "task_id": message.get("task_id"),
            "machine_id": machine_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await manager.send_to_user(user_id, dashboard_message)
        print(f"Forwarded waiting for input notification to user {user_id}")
        
    except Exception as e:
        print(f"Error handling waiting for input: {e}")


async def handle_process_health_update(message: dict, user_id: str, machine_id: str):
    """Handle process health update from enhanced command executor"""
    try:
        # Forward health update to user dashboard
        dashboard_message = {
            "type": "process_health_update",
            "task_id": message.get("task_id"),
            "health_status": message.get("health_status"),
            "metrics": message.get("metrics"),
            "machine_id": machine_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await manager.send_to_user(user_id, dashboard_message)
        print(f"Forwarded process health update to user {user_id}")
        
    except Exception as e:
        print(f"Error handling process health update: {e}")


async def handle_alternative_command_triggered(message: dict, user_id: str, machine_id: str):
    """Handle alternative command triggered notification"""
    try:
        # Store alternative command attempt in database
        db = await get_database()
        task_id = message.get("task_id")
        
        if task_id:
            # Update task with alternative command attempt
            await db.task_executions.update_one(
                {"task_id": task_id},
                {"$push": {
                    "alternative_attempts": {
                        "original_command": message.get("original_command"),
                        "alternative_command": message.get("alternative_command"),
                        "reason": message.get("reason"),
                        "attempt_number": message.get("attempt_number"),
                        "timestamp": datetime.utcnow()
                    }
                }}
            )
        
        # Forward to user dashboard
        dashboard_message = {
            "type": "alternative_command_triggered",
            "task_id": task_id,
            "original_command": message.get("original_command"),
            "alternative_command": message.get("alternative_command"),
            "reason": message.get("reason"),
            "attempt_number": message.get("attempt_number"),
            "machine_id": machine_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await manager.send_to_user(user_id, dashboard_message)
        print(f"Forwarded alternative command trigger to user {user_id}")
        
    except Exception as e:
        print(f"Error handling alternative command triggered: {e}")


async def handle_alternative_command_result(message: dict, user_id: str, machine_id: str):
    """Handle alternative command execution result"""
    try:
        # Store alternative command result in database
        db = await get_database()
        task_id = message.get("task_id")
        
        if task_id:
            # Find the latest alternative attempt and update it with results
            await db.task_executions.update_one(
                {
                    "task_id": task_id,
                    "alternative_attempts.attempt_number": message.get("attempt_number")
                },
                {"$set": {
                    "alternative_attempts.$.result": {
                        "stdout": message.get("stdout"),
                        "stderr": message.get("stderr"),
                        "exit_code": message.get("exit_code"),
                        "completed_at": datetime.utcnow()
                    }
                }}
            )
        
        # Forward to user dashboard
        dashboard_message = {
            "type": "alternative_command_result",
            "task_id": task_id,
            "command": message.get("command"),
            "stdout": message.get("stdout"),
            "stderr": message.get("stderr"),
            "exit_code": message.get("exit_code"),
            "attempt_number": message.get("attempt_number"),
            "machine_id": machine_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await manager.send_to_user(user_id, dashboard_message)
        print(f"Forwarded alternative command result to user {user_id}")
        
    except Exception as e:
        print(f"Error handling alternative command result: {e}")


async def handle_ai_summary_update(message: dict, user_id: str, machine_id: str):
    """Handle AI summary generation/update"""
    try:
        # Store AI summary in database
        db = await get_database()
        task_id = message.get("task_id")
        
        if task_id:
            # Update task with AI summary
            await db.task_executions.update_one(
                {"task_id": task_id},
                {"$set": {
                    "ai_summary": message.get("ai_summary"),
                    "ai_summary_generated_at": datetime.utcnow()
                }}
            )
        
        # Forward to user dashboard
        dashboard_message = {
            "type": "ai_summary_update",
            "task_id": task_id,
            "ai_summary": message.get("ai_summary"),
            "machine_id": machine_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await manager.send_to_user(user_id, dashboard_message)
        print(f"Forwarded AI summary update to user {user_id}")
        
    except Exception as e:
        print(f"Error handling AI summary update: {e}")


async def handle_client_log(message: dict, user_id: str, machine_id: str):
    """Handle detailed client-side execution logs"""
    try:
        task_id = message.get("task_id", "system")
        level = message.get("level", "info")
        logger_name = message.get("logger", "client")
        log_message = message.get("message", "")
        context = message.get("context", {})
        timestamp = message.get("timestamp") or datetime.utcnow().isoformat()
        
        # Add machine_id to context
        context["machine_id"] = machine_id
        
        # Log to server-side log broadcaster
        await log_broadcaster.log_server_event(
            task_id=task_id,
            level=level,
            message=f"[Client] {log_message}",
            details={
                "logger": logger_name,
                "source": "client",
                "context": context,
                "raw_message": message
            },
            context={
                "service": "client_logger",
                "machine_id": machine_id
            }
        )
        
        # Forward client log to user dashboard
        dashboard_message = {
            "type": "client_log",
            "task_id": task_id,
            "level": level,
            "message": log_message,
            "logger": logger_name,
            "context": context,
            "machine_id": machine_id,
            "timestamp": timestamp
        }
        
        await manager.send_to_user(user_id, dashboard_message)
        print(f"Forwarded client log to user {user_id}: [{level}] {log_message}")
        
    except Exception as e:
        print(f"Error handling client log: {e}")


async def send_ai_summary_to_user(user_id: str, task_id: str, ai_summary: str, machine_id: str):
    """Helper function to send AI summary updates to user"""
    try:
        dashboard_message = {
            "type": "ai_summary_update",
            "task_id": task_id,
            "ai_summary": ai_summary,
            "machine_id": machine_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await manager.send_to_user(user_id, dashboard_message)
        print(f"Sent AI summary update to user {user_id} for task {task_id}")
        
    except Exception as e:
        print(f"Error sending AI summary to user: {e}")