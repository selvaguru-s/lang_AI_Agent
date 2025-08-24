# AI Linux Agent - Complete API Documentation

## 🌐 **API Overview**

The AI Linux Agent backend provides a comprehensive REST API and WebSocket interface for managing remote Linux systems with AI-powered intelligence. The API is built with FastAPI and includes real-time communication, authentication, and advanced command processing capabilities.

**Base URL**: `http://localhost:8000/api` (Development)  
**WebSocket URL**: `ws://localhost:8000/ws` (Development)

## 🔐 **Authentication**

All API endpoints require authentication using either:
1. **Firebase ID Token** (for login endpoints)
2. **API Key** (for all other endpoints)

### Authentication Header
```
Authorization: Bearer <API_KEY>
```

### Rate Limiting
- **Default**: 100 requests per minute per IP
- **Authenticated**: 1000 requests per minute per user
- **WebSocket**: 50 connections per user

## 📚 **API Endpoints Reference**

### **Authentication Endpoints**

#### `POST /api/auth/login`
Authenticate user with Firebase ID token and receive API key.

**Request Body:**
```json
{
  "id_token": "firebase_id_token_here"
}
```

**Response:**
```json
{
  "user_id": "507f1f77bcf86cd799439011",
  "email": "user@example.com",
  "api_key": "ak_1234567890abcdef",
  "expires_in": 3600
}
```

#### `POST /api/auth/refresh`
Refresh user session with new Firebase ID token.

**Request Body:**
```json
{
  "id_token": "new_firebase_id_token"
}
```

**Response:**
```json
{
  "user_id": "507f1f77bcf86cd799439011",
  "api_key": "ak_1234567890abcdef",
  "expires_in": 3600
}
```

---

### **Client Management Endpoints**

#### `POST /api/clients/register`
Register a new Linux client machine.

**Request Body:**
```json
{
  "machine_id": "unique_machine_identifier",
  "hostname": "server01.example.com",
  "os": "Ubuntu 22.04.3 LTS",
  "arch": "x86_64",
  "mac_address": "00:11:22:33:44:55"
}
```

**Response:**
```json
{
  "machine_id": "unique_machine_identifier",
  "status": "registered",
  "message": "Client registered successfully"
}
```

#### `GET /api/clients/list`
Get list of all registered client machines for the authenticated user.

**Response:**
```json
{
  "clients": [
    {
      "machine_id": "machine_001",
      "hostname": "web-server-01",
      "os_info": "Ubuntu 22.04.3 LTS",
      "architecture": "x86_64",
      "last_seen": "2024-01-15T10:30:00Z",
      "is_active": true,
      "status": "online"
    },
    {
      "machine_id": "machine_002",
      "hostname": "db-server-01", 
      "os_info": "CentOS 8",
      "architecture": "x86_64",
      "last_seen": "2024-01-15T10:25:00Z",
      "is_active": false,
      "status": "offline"
    }
  ],
  "total": 2,
  "active": 1
}
```

#### `GET /api/clients/{machine_id}`
Get detailed information about a specific client machine.

**Response:**
```json
{
  "machine_id": "machine_001",
  "hostname": "web-server-01",
  "os_info": "Ubuntu 22.04.3 LTS",
  "architecture": "x86_64",
  "mac_address": "00:11:22:33:44:55",
  "last_seen": "2024-01-15T10:30:00Z",
  "is_active": true,
  "system_metrics": {
    "cpu_usage": 15.5,
    "memory_usage": 68.2,
    "disk_usage": 45.0,
    "load_average": [0.5, 0.8, 1.2]
  },
  "recent_tasks": 5,
  "success_rate": 95.2
}
```

#### `DELETE /api/clients/{machine_id}`
Remove a client machine from the user's account.

**Response:**
```json
{
  "message": "Client removed successfully",
  "machine_id": "machine_001"
}
```

#### `POST /api/clients/{machine_id}/ping`
Send a ping command to test client connectivity.

**Response:**
```json
{
  "machine_id": "machine_001",
  "status": "online",
  "response_time": 150,
  "last_ping": "2024-01-15T10:30:00Z"
}
```

---

### **Task Management Endpoints**

#### `POST /api/tasks`
Create and execute a new task on a target machine.

**Request Body:**
```json
{
  "prompt": "Install nginx and configure it for production",
  "machine_id": "machine_001"
}
```

**Response:**
```json
{
  "task_id": "task_550e8400-e29b-41d4-a716-446655440000",
  "status": "running",
  "subtasks": [
    {
      "id": "task_1",
      "description": "Check if nginx is already installed",
      "command": "which nginx",
      "expected_output": "Command should return nginx path or exit with code 1 if not found"
    },
    {
      "id": "task_2", 
      "description": "Install nginx using package manager",
      "command": "apt update && apt install -y nginx",
      "expected_output": "Package installation should complete successfully"
    },
    {
      "id": "task_3",
      "description": "Configure nginx for production",
      "command": "nginx -t && systemctl enable nginx",
      "expected_output": "Configuration test should pass and service should be enabled"
    }
  ]
}
```

#### `GET /api/tasks/list`
Get paginated list of tasks for the authenticated user.

**Query Parameters:**
- `limit` (optional): Number of tasks to return (default: 20)
- `offset` (optional): Number of tasks to skip (default: 0)
- `status` (optional): Filter by task status (pending, running, completed, failed)
- `machine_id` (optional): Filter by machine ID

**Response:**
```json
{
  "tasks": [
    {
      "task_id": "task_550e8400-e29b-41d4-a716-446655440000",
      "original_prompt": "Install nginx and configure it",
      "status": "completed",
      "machine_id": "machine_001",
      "created_at": "2024-01-15T10:00:00Z",
      "completed_at": "2024-01-15T10:05:30Z",
      "current_subtask_index": 3,
      "total_subtasks": 3,
      "success_rate": 100.0,
      "ai_summary": "Successfully installed and configured nginx on Ubuntu server."
    }
  ],
  "total": 1,
  "limit": 20,
  "offset": 0
}
```

#### `GET /api/tasks/{task_id}`
Get detailed information about a specific task including execution history.

**Response:**
```json
{
  "task_id": "task_550e8400-e29b-41d4-a716-446655440000",
  "user_id": "507f1f77bcf86cd799439011",
  "machine_id": "machine_001",
  "original_prompt": "Install nginx and configure it",
  "status": "completed",
  "created_at": "2024-01-15T10:00:00Z",
  "completed_at": "2024-01-15T10:05:30Z",
  "current_subtask_index": 3,
  "ai_summary": "Successfully installed and configured nginx server with production-ready settings.",
  "subtasks": [
    {
      "id": "task_1",
      "description": "Check if nginx is already installed",
      "command": "which nginx",
      "expected_output": "Command should return nginx path or exit with code 1",
      "attempts": [
        {
          "attempt_number": 1,
          "command": "which nginx",
          "output": "",
          "exit_code": 1,
          "validation_result": {
            "is_valid": true,
            "confidence": 0.9,
            "error_message": "",
            "should_retry": false
          },
          "timestamp": "2024-01-15T10:00:05Z"
        }
      ]
    }
  ]
}
```

#### `GET /api/tasks/status/{task_id}`
Get current status of a running task.

**Response:**
```json
{
  "task_id": "task_550e8400-e29b-41d4-a716-446655440000",
  "status": "running",
  "current_subtask_index": 1,
  "total_subtasks": 3,
  "progress_percentage": 33.3,
  "estimated_completion": "2024-01-15T10:08:00Z",
  "error_message": null
}
```

#### `DELETE /api/tasks/{task_id}`
Cancel a running task.

**Response:**
```json
{
  "message": "Task cancelled successfully",
  "task_id": "task_550e8400-e29b-41d4-a716-446655440000"
}
```

#### `POST /api/tasks/{task_id}/generate-summary`
Generate or regenerate AI summary for a completed task.

**Response:**
```json
{
  "message": "AI summary generated successfully",
  "ai_summary": "The task successfully installed nginx web server and configured it with production settings. All subtasks completed without errors."
}
```

---

### **Command Utilities Endpoints**

#### `POST /api/commands/generate-alternatives`
Generate alternative commands when primary command fails.

**Request Body:**
```json
{
  "original_command": "apt install broken-package",
  "failure_reason": "Package not found in repository",
  "system_info": {
    "os": "Ubuntu 22.04",
    "arch": "x86_64"
  },
  "process_metrics": {
    "cpu_usage": 0.1,
    "memory_usage": 45.2,
    "execution_time": 30
  }
}
```

**Response:**
```json
{
  "alternatives": [
    {
      "command": "apt update && apt install broken-package",
      "description": "Update package lists before installation",
      "reason": "Package lists might be outdated",
      "confidence": 0.8,
      "estimated_success_rate": 0.7
    },
    {
      "command": "apt search broken-package",
      "description": "Search for similar package names",
      "reason": "Package name might be incorrect",
      "confidence": 0.6,
      "estimated_success_rate": 0.9
    }
  ],
  "strategy_explanation": "Generated alternatives focus on common package installation issues",
  "fallback_available": true
}
```

#### `POST /api/commands/analyze-hanging`
Analyze why a command might be hanging and get intervention recommendations.

**Request Body:**
```json
{
  "command": "wget https://slow-server.com/large-file.zip",
  "output_so_far": "Connecting to slow-server.com...",
  "process_metrics": {
    "cpu_usage": 0.0,
    "memory_usage": 12.5,
    "network_activity": 0,
    "execution_time": 120
  }
}
```

**Response:**
```json
{
  "likely_cause": "Network timeout or slow server response",
  "confidence": 0.85,
  "recommended_action": "alternative",
  "intervention_command": "timeout 60 wget https://slow-server.com/large-file.zip",
  "wait_time_suggestion": "30",
  "explanation": "The command appears to be hanging on network connection with no recent activity. Alternative command with timeout is recommended."
}
```

#### `GET /api/commands/command-patterns`
Get information about command classification and timeout patterns.

**Response:**
```json
{
  "command_types": {
    "quick_info": {
      "patterns": ["ls", "pwd", "whoami", "date"],
      "no_output_timeout": 10,
      "max_total_timeout": 30
    },
    "package_management": {
      "patterns": ["apt", "yum", "pip", "npm install"],
      "no_output_timeout": 60,
      "max_total_timeout": 600
    },
    "network_operations": {
      "patterns": ["wget", "curl", "ssh", "scp"],
      "no_output_timeout": 45,
      "max_total_timeout": 300
    }
  },
  "total_patterns": 45
}
```

#### `GET /api/commands/health-metrics`
Get monitoring configuration and health check information.

**Response:**
```json
{
  "monitoring_config": {
    "health_check_interval": 5,
    "hanging_detection_threshold": 45,
    "memory_limit_mb": 1024,
    "cpu_threshold_percent": 90
  },
  "health_states": [
    "HEALTHY",
    "IDLE", 
    "HANGING",
    "WAITING_INPUT",
    "ERROR_LOOP"
  ],
  "escalation_levels": [
    "monitor",
    "warn", 
    "suggest_alternative",
    "execute_alternative",
    "terminate"
  ]
}
```

---

## 📡 **WebSocket API**

### **Connection Endpoints**

#### Client Connection: `ws://localhost:8000/ws/client`
Used by Python clients to connect to the backend.

**Query Parameters:**
- `api_key`: User's API key
- `machine_id`: Unique machine identifier

**Connection Flow:**
1. Client connects with valid API key and machine ID
2. Backend validates authentication
3. Connection registered in connection manager
4. Client begins sending heartbeat messages

#### Dashboard Connection: `ws://localhost:8000/ws/dashboard`
Used by web dashboard for real-time updates.

**Query Parameters:**
- `api_key`: User's API key

### **WebSocket Message Types**

#### **Client → Backend Messages**

**Heartbeat Message:**
```json
{
  "type": "heartbeat",
  "timestamp": "2024-01-15T10:30:00Z",
  "machine_id": "machine_001"
}
```

**Command Result Message:**
```json
{
  "type": "command_result",
  "task_id": "task_550e8400-e29b-41d4-a716-446655440000",
  "subtask_id": "task_1",
  "command": "which nginx",
  "output": "/usr/sbin/nginx",
  "exit_code": 0,
  "attempt_number": 1,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Live Output Message:**
```json
{
  "type": "live_output",
  "task_id": "task_550e8400-e29b-41d4-a716-446655440000",
  "subtask_id": "task_2",
  "attempt_number": 1,
  "stream": "stdout",
  "data": "Reading package lists... Done\n",
  "timestamp": "2024-01-15T10:30:05Z"
}
```

**System Info Update:**
```json
{
  "type": "system_info_update",
  "machine_id": "machine_001",
  "system_info": {
    "os": "Ubuntu 22.04.3 LTS",
    "arch": "x86_64",
    "hostname": "web-server-01",
    "cpu_usage": 15.5,
    "memory_usage": 68.2,
    "disk_usage": 45.0
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Interactive Prompt:**
```json
{
  "type": "interactive_prompt",
  "task_id": "task_550e8400-e29b-41d4-a716-446655440000",
  "data": "[sudo] password for user: ",
  "timestamp": "2024-01-15T10:30:10Z"
}
```

**Process Health Update:**
```json
{
  "type": "process_health_update",
  "task_id": "task_550e8400-e29b-41d4-a716-446655440000",
  "health_status": "HEALTHY",
  "metrics": {
    "cpu_usage": 25.5,
    "memory_usage": 128.0,
    "execution_time": 45,
    "output_activity": true
  },
  "timestamp": "2024-01-15T10:30:15Z"
}
```

#### **Backend → Client Messages**

**Execute Command:**
```json
{
  "type": "execute_command",
  "task_id": "task_550e8400-e29b-41d4-a716-446655440000",
  "subtask_id": "task_1",
  "command": "which nginx",
  "attempt_number": 1
}
```

**Kill Task:**
```json
{
  "type": "kill_task",
  "task_id": "task_550e8400-e29b-41d4-a716-446655440000"
}
```

**User Input:**
```json
{
  "type": "user_input",
  "task_id": "task_550e8400-e29b-41d4-a716-446655440000",
  "input": "password123"
}
```

**Ping:**
```json
{
  "type": "ping",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### **Backend → Dashboard Messages**

**Task Update:**
```json
{
  "type": "task_update",
  "task_id": "task_550e8400-e29b-41d4-a716-446655440000",
  "subtask_id": "task_1",
  "status": "running",
  "attempt": {
    "attempt_number": 1,
    "command": "which nginx",
    "output": "",
    "exit_code": 1,
    "timestamp": "2024-01-15T10:30:00Z"
  },
  "validation": {
    "is_valid": true,
    "confidence": 0.9,
    "should_retry": false
  }
}
```

**Live Output Forward:**
```json
{
  "type": "live_output",
  "task_id": "task_550e8400-e29b-41d4-a716-446655440000",
  "subtask_id": "task_2",
  "attempt_number": 1,
  "stream": "stdout",
  "data": "Installing nginx...\n",
  "machine_id": "machine_001",
  "timestamp": "2024-01-15T10:30:05Z"
}
```

**AI Summary Update:**
```json
{
  "type": "ai_summary_update",
  "task_id": "task_550e8400-e29b-41d4-a716-446655440000",
  "ai_summary": "Successfully installed nginx and configured production settings.",
  "machine_id": "machine_001",
  "timestamp": "2024-01-15T10:35:00Z"
}
```

**Alternative Command Triggered:**
```json
{
  "type": "alternative_command_triggered",
  "task_id": "task_550e8400-e29b-41d4-a716-446655440000",
  "original_command": "wget slow-server.com/file.zip",
  "alternative_command": "curl -O slow-server.com/file.zip",
  "reason": "Command hanging detected - no activity for 45 seconds",
  "attempt_number": 2,
  "machine_id": "machine_001",
  "timestamp": "2024-01-15T10:32:00Z"
}
```

## 🚨 **Error Handling**

### **HTTP Error Codes**

- **400 Bad Request**: Invalid request data or parameters
- **401 Unauthorized**: Missing or invalid authentication
- **403 Forbidden**: Insufficient permissions for resource
- **404 Not Found**: Requested resource does not exist
- **422 Unprocessable Entity**: Validation errors in request data
- **429 Too Many Requests**: Rate limit exceeded
- **500 Internal Server Error**: Server-side error occurred

### **Error Response Format**

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "The provided command contains dangerous operations",
    "details": {
      "field": "command",
      "rejected_operations": ["rm -rf /", "sudo shutdown"],
      "suggestion": "Use specific file paths instead of recursive deletion"
    },
    "timestamp": "2024-01-15T10:30:00Z",
    "request_id": "req_123456789"
  }
}
```

### **WebSocket Error Handling**

**Connection Errors:**
- **4001**: Invalid API key
- **4002**: Machine not found  
- **4003**: Machine not authorized for user
- **4004**: Connection limit exceeded

**Message Errors:**
```json
{
  "type": "error",
  "error_code": "COMMAND_EXECUTION_FAILED",
  "message": "Command execution failed after 3 attempts",
  "task_id": "task_550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## 🔧 **SDK Integration Examples**

### **Python Client Example**
```python
import asyncio
import websockets
import json

async def connect_client():
    uri = "ws://localhost:8000/ws/client?api_key=ak_123&machine_id=machine_001"
    
    async with websockets.connect(uri) as websocket:
        # Send heartbeat
        heartbeat = {
            "type": "heartbeat",
            "timestamp": "2024-01-15T10:30:00Z",
            "machine_id": "machine_001"
        }
        await websocket.send(json.dumps(heartbeat))
        
        # Listen for commands
        async for message in websocket:
            data = json.loads(message)
            if data["type"] == "execute_command":
                # Execute command and send result
                pass

asyncio.run(connect_client())
```

### **JavaScript Frontend Example**
```javascript
class AILinuxAgentClient {
  constructor(apiKey) {
    this.apiKey = apiKey;
    this.baseURL = 'http://localhost:8000/api';
    this.wsURL = 'ws://localhost:8000/ws/dashboard';
  }

  async createTask(prompt, machineId) {
    const response = await fetch(`${this.baseURL}/tasks`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.apiKey}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ prompt, machine_id: machineId })
    });
    
    return await response.json();
  }

  connectWebSocket() {
    this.ws = new WebSocket(`${this.wsURL}?api_key=${this.apiKey}`);
    
    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      this.handleMessage(data);
    };
  }

  handleMessage(data) {
    switch (data.type) {
      case 'live_output':
        this.displayLiveOutput(data);
        break;
      case 'task_update':
        this.updateTaskStatus(data);
        break;
    }
  }
}
```

This comprehensive API documentation provides everything needed to integrate with and extend the AI Linux Agent system. The API is designed for both human developers and automated systems, with comprehensive error handling and real-time capabilities.