import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from fastapi import WebSocket

logger = logging.getLogger(__name__)


class LogBroadcaster:
    """
    Service for broadcasting system logs to connected WebSocket clients
    in real-time for the TaskDetails log viewer
    """
    
    def __init__(self):
        self.connected_clients: Dict[str, WebSocket] = {}
        self.task_subscribers: Dict[str, List[str]] = {}  # task_id -> [client_ids]
        self.log_history: Dict[str, List[Dict[str, Any]]] = {}  # task_id -> logs
        self.max_history_per_task = 500
        
    async def connect_client(self, client_id: str, websocket: WebSocket, task_id: str = None):
        """Connect a client to log broadcasting"""
        self.connected_clients[client_id] = websocket
        
        if task_id:
            if task_id not in self.task_subscribers:
                self.task_subscribers[task_id] = []
            self.task_subscribers[task_id].append(client_id)
            
            # Send recent log history for this task
            if task_id in self.log_history:
                for log_entry in self.log_history[task_id][-50:]:  # Send last 50 logs
                    await self._send_to_client(client_id, {
                        "type": "server_log",
                        **log_entry
                    })
        
        logger.info(f"LogBroadcaster: Client {client_id} connected for task {task_id}")
    
    async def disconnect_client(self, client_id: str):
        """Disconnect a client from log broadcasting"""
        if client_id in self.connected_clients:
            del self.connected_clients[client_id]
            
            # Remove from task subscribers
            for task_id, subscribers in self.task_subscribers.items():
                if client_id in subscribers:
                    subscribers.remove(client_id)
                    
            logger.info(f"LogBroadcaster: Client {client_id} disconnected")
    
    async def log_server_event(self, task_id: str, level: str, message: str, 
                             details: Dict[str, Any] = None, context: Dict[str, Any] = None):
        """Log a server-side event and broadcast to subscribers"""
        
        log_entry = {
            "source": "server",
            "level": level,
            "message": message,
            "details": details or {},
            "context": context or {},
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "task_id": task_id
        }
        
        # Store in history
        if task_id not in self.log_history:
            self.log_history[task_id] = []
        
        self.log_history[task_id].append(log_entry)
        
        # Limit history size
        if len(self.log_history[task_id]) > self.max_history_per_task:
            self.log_history[task_id] = self.log_history[task_id][-self.max_history_per_task:]
        
        # Broadcast to subscribers
        await self._broadcast_to_task_subscribers(task_id, {
            "type": "server_log",
            **log_entry
        })
        
        # Also log to Python logger
        getattr(logger, level.lower(), logger.info)(
            f"Task {task_id}: {message}", extra={"details": details, "context": context}
        )
    
    async def log_llm_analysis(self, task_id: str, analysis: Dict[str, Any], 
                              command: str = None, output: str = None):
        """Log LLM analysis results"""
        
        await self.log_server_event(
            task_id=task_id,
            level="info",
            message="LLM analysis completed",
            details={
                "analysis_result": analysis,
                "command_analyzed": command,
                "output_analyzed": output and output[:500] + "..." if len(output or "") > 500 else output
            },
            context={
                "service": "llm_monitor",
                "analysis_type": "command_health"
            }
        )
        
        # Send specific LLM analysis event
        await self._broadcast_to_task_subscribers(task_id, {
            "type": "llm_analysis",
            "task_id": task_id,
            "analysis": analysis,
            "command": command,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        })
    
    async def log_alternative_execution(self, task_id: str, original_command: str, 
                                      alternative_command: str, reason: str, attempt_number: int = 1):
        """Log alternative command execution"""
        
        await self.log_server_event(
            task_id=task_id,
            level="warning", 
            message=f"Executing alternative command (attempt {attempt_number})",
            details={
                "original_command": original_command,
                "alternative_command": alternative_command,
                "reason": reason,
                "attempt_number": attempt_number
            },
            context={
                "service": "command_executor",
                "action": "alternative_execution"
            }
        )
        
        # Send specific alternative execution event
        await self._broadcast_to_task_subscribers(task_id, {
            "type": "alternative_execution",
            "task_id": task_id,
            "original_command": original_command,
            "alternative_command": alternative_command,
            "reason": reason,
            "attempt_number": attempt_number,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        })
    
    async def log_command_killed(self, task_id: str, command: str, reason: str, 
                                suggested_alternative: str = None, execution_time: float = None):
        """Log command termination"""
        
        await self.log_server_event(
            task_id=task_id,
            level="warning",
            message=f"Command terminated: {reason}",
            details={
                "terminated_command": command,
                "termination_reason": reason,
                "suggested_alternative": suggested_alternative,
                "execution_time_seconds": execution_time
            },
            context={
                "service": "process_monitor",
                "action": "command_termination"
            }
        )
        
        # Send specific command killed event
        await self._broadcast_to_task_subscribers(task_id, {
            "type": "command_killed",
            "task_id": task_id,
            "command": command,
            "reason": reason,
            "suggested_alternative": suggested_alternative,
            "execution_time": execution_time,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        })
    
    async def log_task_chain_progress(self, task_id: str, completed_subtasks: int, 
                                    total_subtasks: int, current_result: Dict[str, Any] = None):
        """Log task chain progress"""
        
        await self.log_server_event(
            task_id=task_id,
            level="info",
            message=f"Task chain progress: {completed_subtasks}/{total_subtasks} completed",
            details={
                "completed_subtasks": completed_subtasks,
                "total_subtasks": total_subtasks,
                "progress_percentage": round((completed_subtasks / total_subtasks) * 100, 1),
                "current_result": current_result
            },
            context={
                "service": "task_executor",
                "action": "chain_progress"
            }
        )
        
        # Send specific task chain progress event
        await self._broadcast_to_task_subscribers(task_id, {
            "type": "task_chain_progress",
            "task_id": task_id,
            "completed_subtasks": completed_subtasks,
            "total_subtasks": total_subtasks,
            "current_result": current_result,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        })
    
    async def log_websocket_event(self, task_id: str, event_type: str, message: str, 
                                 client_info: Dict[str, Any] = None):
        """Log WebSocket events"""
        
        await self.log_server_event(
            task_id=task_id,
            level="debug",
            message=f"WebSocket {event_type}: {message}",
            details={
                "event_type": event_type,
                "client_info": client_info or {}
            },
            context={
                "service": "websocket",
                "action": event_type
            }
        )
        
        # Send WebSocket event
        await self._broadcast_to_task_subscribers(task_id, {
            "type": "websocket_event",
            "task_id": task_id,
            "event_type": event_type,
            "message": message,
            "client_info": client_info,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        })
    
    async def _broadcast_to_task_subscribers(self, task_id: str, message: Dict[str, Any]):
        """Broadcast message to all subscribers of a specific task"""
        
        if task_id not in self.task_subscribers:
            return
            
        subscribers = self.task_subscribers[task_id].copy()  # Copy to avoid modification during iteration
        
        for client_id in subscribers:
            await self._send_to_client(client_id, message)
    
    async def _send_to_client(self, client_id: str, message: Dict[str, Any]):
        """Send message to a specific client"""
        
        if client_id not in self.connected_clients:
            return
            
        try:
            websocket = self.connected_clients[client_id]
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Failed to send message to client {client_id}: {e}")
            # Remove disconnected client
            await self.disconnect_client(client_id)
    
    async def get_task_log_history(self, task_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get log history for a specific task"""
        
        if task_id not in self.log_history:
            return []
            
        return self.log_history[task_id][-limit:]
    
    async def clear_task_logs(self, task_id: str):
        """Clear logs for a specific task"""
        
        if task_id in self.log_history:
            del self.log_history[task_id]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get broadcaster statistics"""
        
        return {
            "connected_clients": len(self.connected_clients),
            "active_tasks": len(self.task_subscribers),
            "total_logs_stored": sum(len(logs) for logs in self.log_history.values()),
            "tasks_with_subscribers": {
                task_id: len(subscribers) 
                for task_id, subscribers in self.task_subscribers.items() 
                if subscribers
            }
        }


# Global log broadcaster instance
log_broadcaster = LogBroadcaster()