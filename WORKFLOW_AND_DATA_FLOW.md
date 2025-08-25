# AI Linux Agent - Workflow and Data Flow

## Overview

This document details the complete workflows and data flows within the AI Linux Agent system, from user authentication to task execution and monitoring.

## 1. User Authentication Workflow

### 1.1 Initial Authentication Flow
```
User → Frontend → Firebase → Backend → Database
  1. User clicks "Login with Google"
  2. Frontend initiates Firebase authentication
  3. Firebase returns ID token
  4. Frontend sends ID token to backend /api/auth/login
  5. Backend validates token with Firebase Admin SDK
  6. Backend creates/updates user record in MongoDB
  7. Backend generates unique API key for user
  8. Backend returns user data and API key
  9. Frontend stores user data and API key in Pinia store
  10. Frontend establishes WebSocket connection with API key
```

### 1.2 Subsequent Authentication Flow
```
User → Frontend → Local Storage → Backend
  1. User visits application
  2. Frontend checks local storage for user data
  3. If found, attempts to connect WebSocket with stored API key
  4. Backend validates API key against database
  5. If valid, user is authenticated; if invalid, redirect to login
```

## 2. Client Registration Workflow

### 2.1 First-Time Client Setup
```
Client Machine → Backend → Database
  1. Client generates unique machine ID using hostname + MAC address
  2. Client saves machine ID to local config/machine_id file
  3. Client connects to backend via WebSocket with API key
  4. Client sends system_info_update message with OS details
  5. Backend registers client machine in database
  6. Backend associates machine with user account
  7. Backend confirms registration via WebSocket
```

### 2.2 Client Reconnection Flow
```
Client Machine → Backend → Database
  1. Client reads existing machine ID from config file
  2. Client establishes WebSocket connection with API key + machine ID
  3. Backend validates client and updates last_seen timestamp
  4. Client sends heartbeat messages every 30 seconds
  5. Backend maintains client as active in database
```

## 3. Task Creation and Execution Workflow

### 3.1 Task Creation Flow
```
User → Frontend → Backend → LLM Service → Database → Client
  1. User enters natural language prompt in frontend
  2. User selects target client machine
  3. Frontend sends POST /api/tasks with prompt and machine_id
  4. Backend validates user permissions for selected machine
  5. Backend calls LLM service to decompose task into subtasks
  6. LLM service returns structured subtasks with Linux commands
  7. Backend creates TaskExecution record in database
  8. Backend attempts to start task execution on target client
  9. Backend returns task_id and initial status to frontend
```

### 3.2 Task Execution Flow
```
Backend → Client → Backend → Database → Frontend
  1. Backend sends execute_command message to target client via WebSocket
  2. Client receives command and logs execution start
  3. Client executes Linux command using asyncio subprocess
  4. Client captures stdout, stderr, and exit code
  5. Client sends command_result back to backend via WebSocket
  6. Backend receives result and validates output using LLM service
  7. Backend updates subtask attempt in database
  8. Backend determines next action (continue, retry, or fail)
  9. Backend broadcasts task_status_update to frontend via WebSocket
  10. Process repeats for each subtask until task completion
```

### 3.3 Task Validation and Retry Flow
```
Backend → LLM Service → Backend → Client
  1. Backend receives command result from client
  2. Backend calls LLM service to validate output
  3. LLM service analyzes exit code, output, and expected results
  4. If validation fails, LLM suggests alternative command or retry
  5. Backend decides whether to retry (max 3 attempts per subtask)
  6. If retrying, sends new execute_command to client
  7. If max attempts reached, marks subtask as failed
  8. Backend updates task status and notifies frontend
```

## 4. Real-Time Communication Data Flow

### 4.1 WebSocket Message Types and Flow

#### Frontend ↔ Backend Messages
- **Connection**: Frontend connects with API key for authentication
- **task_status_update**: Backend → Frontend (task progress updates)
- **client_status_update**: Backend → Frontend (client online/offline status)
- **ai_summary_update**: Backend → Frontend (AI-generated task summaries)

#### Client ↔ Backend Messages
- **Connection**: Client connects with API key + machine_id
- **system_info_update**: Client → Backend (OS and hardware details)
- **heartbeat**: Client → Backend (connection keep-alive every 30s)
- **execute_command**: Backend → Client (command to execute)
- **command_result**: Client → Backend (command execution results)
- **client_log**: Client → Backend (detailed execution logs)

### 4.2 Heartbeat and Connection Management
```
Every 30 seconds:
Client → Backend: {"type": "heartbeat", "timestamp": "ISO-timestamp"}
Backend → Database: Update client last_seen timestamp

On connection loss:
Backend marks client as inactive
Frontend shows client as offline
Pending tasks are marked as failed
```

## 5. Data Flow Diagrams

### 5.1 Task Execution Data Flow
```
[User Input] → [Frontend] → [Backend API]
                                ↓
[LLM Service] ← [Task Decomposition]
    ↓
[Structured Subtasks] → [Database Storage]
    ↓
[WebSocket] → [Client Agent] → [Linux Command Execution]
    ↓
[Command Results] → [WebSocket] → [Backend Validation]
    ↓
[LLM Validation] → [Database Update] → [Frontend Update]
```

### 5.2 Client Management Data Flow
```
[Client Startup] → [Machine ID Generation] → [WebSocket Connection]
    ↓
[Authentication] → [Registration] → [Database Storage]
    ↓
[Heartbeat Loop] → [Status Updates] → [Connection Monitoring]
    ↓
[Task Assignment] → [Command Execution] → [Result Reporting]
```

## 6. Database Operations Flow

### 6.1 Read Operations
- **User Authentication**: Validate API keys and retrieve user data
- **Client Listing**: Fetch user's registered client machines
- **Task History**: Retrieve user's task execution history
- **Task Details**: Fetch complete task information including subtasks

### 6.2 Write Operations
- **User Registration**: Create/update user records and API keys
- **Client Registration**: Store client machine information
- **Task Creation**: Insert new TaskExecution records
- **Status Updates**: Update task and subtask status throughout execution
- **Logging**: Store client logs and execution attempts

### 6.3 MongoDB Document Updates
```javascript
// Task execution updates
{
  $set: {
    "status": "running",
    "current_subtask_index": 1,
    "subtasks.0.status": "completed",
    "subtasks.0.attempts": [/* attempt objects */]
  }
}

// Client status updates
{
  $set: {
    "last_seen": new Date(),
    "is_active": true
  }
}
```

## 7. Error Handling and Recovery Workflows

### 7.1 Client Disconnection Handling
```
1. Backend detects client disconnection
2. Mark client as inactive in database
3. Mark any running tasks as "failed" with error message
4. Notify frontend of client status change
5. When client reconnects, update status to active
6. Allow new task assignments
```

### 7.2 Command Execution Failures
```
1. Client executes command and gets non-zero exit code
2. Client sends result to backend with exit code and error output
3. Backend calls LLM service for validation
4. LLM determines if failure is expected (e.g., status checks) or actual failure
5. If actual failure, LLM suggests alternative command
6. Backend retries with alternative (up to 3 attempts)
7. If all attempts fail, mark subtask as failed and continue or abort task
```

### 7.3 Backend Service Recovery
```
1. Database connection loss:
   - Reconnect with exponential backoff
   - Queue operations until connection restored
   - Notify clients of temporary unavailability

2. LLM service failure:
   - Retry with exponential backoff
   - Use fallback validation for simple cases
   - Mark complex validations as uncertain

3. WebSocket connection issues:
   - Client implements automatic reconnection
   - Backend maintains connection state
   - Resume task execution after reconnection
```

## 8. Security Data Flow

### 8.1 Authentication Chain
```
Firebase ID Token → Backend Validation → API Key Generation → WebSocket Auth → Command Execution
```

### 8.2 Permission Verification
```
1. User requests action on client machine
2. Backend verifies machine_id in user.client_machines array
3. Backend checks client is active and registered
4. Backend validates user has permission for requested operation
5. Only then proceed with command execution
```

## 9. Monitoring and Logging Flow

### 9.1 Client-Side Logging
```
Client Events → Structured Logs → WebSocket → Backend → Database Storage
- Command execution start/completion
- System status changes
- Error conditions
- Performance metrics
```

### 9.2 System Monitoring
```
- Client heartbeats for connectivity monitoring
- Task execution metrics for performance tracking
- Error rates for system health assessment
- Resource usage monitoring on client machines
```

## 10. AI Integration Workflow

### 10.1 Task Decomposition Process
```
User Prompt → System Context → LLM Service
    ↓
Prompt Engineering → Gemini API Call → JSON Response
    ↓
Validation → Subtask Creation → Command Generation
```

### 10.2 AI Summary Generation
```
Completed Task → All Subtask Results → LLM Service
    ↓
Analysis Prompt → Gemini API → Summary Generation
    ↓
Database Storage → WebSocket Broadcast → Frontend Display
```

This comprehensive workflow documentation provides a complete picture of how data flows through the AI Linux Agent system, enabling better understanding for maintenance, debugging, and feature development.