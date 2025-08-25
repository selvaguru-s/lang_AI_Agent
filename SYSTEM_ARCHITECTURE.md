# AI Linux Agent - System Architecture

## Overview

The AI Linux Agent is a distributed system that enables remote Linux command execution through an AI-powered web interface. The system consists of three main components: a Python FastAPI backend, a Vue.js frontend, and client agents that run on target machines.

## System Components

### 1. Backend API Server (`/backend`)
- **Framework**: FastAPI with Python 3.12
- **Database**: MongoDB with Motor (async driver)
- **Authentication**: Firebase Admin SDK + JWT tokens
- **AI Integration**: Google Gemini 2.0 Flash via LangChain
- **Real-time Communication**: WebSockets
- **Security**: Rate limiting, CORS, custom middleware

### 2. Frontend Web Application (`/frontend`)
- **Framework**: Vue.js 3 with Composition API
- **State Management**: Pinia
- **Routing**: Vue Router with authentication guards
- **UI Framework**: Tailwind CSS + Headless UI
- **Build Tool**: Vite
- **Authentication**: Firebase Web SDK

### 3. Client Agents (`/client`)
- **Runtime**: Python 3.12
- **Communication**: WebSocket client
- **System Integration**: subprocess, psutil for system monitoring
- **Security**: Machine ID-based authentication

## Architecture Patterns

### Client-Server Architecture
- **API Server**: Central hub handling authentication, task management, and client coordination
- **Web Frontend**: User interface for creating tasks and monitoring execution
- **Client Agents**: Lightweight agents running on target machines

### Event-Driven Architecture
- WebSocket connections for real-time communication
- Async/await pattern throughout the system
- Event broadcasting for status updates

### Microservices Pattern (Modular)
- Separate routers for different API concerns (auth, tasks, clients, commands)
- Service layer abstractions (LLM service, database service)
- Independent client agents

## Data Models

### Core Entities

#### User
```python
class User(BaseModel):
    id: PyObjectId
    firebase_uid: str
    email: str
    name: str
    api_key: str
    created_at: datetime
    last_login: datetime
    is_active: bool
    client_machines: List[str]
```

#### Client Machine
```python
class ClientMachine(BaseModel):
    id: PyObjectId
    machine_id: str
    hostname: str
    os_info: str
    architecture: str
    mac_address: str
    last_seen: datetime
    is_active: bool
```

#### Task Execution
```python
class TaskExecution(BaseModel):
    task_id: str
    user_id: str
    machine_id: str
    original_prompt: str
    subtasks: List[dict]
    current_subtask_index: int
    status: str  # pending, running, completed, failed
    created_at: datetime
    completed_at: Optional[datetime]
    error_message: Optional[str]
```

#### Subtask Attempt
```python
class SubtaskAttempt(BaseModel):
    attempt_number: int
    command: str
    output: str
    exit_code: int
    validation_result: dict
    timestamp: datetime
```

## Security Architecture

### Authentication Flow
1. **Frontend**: Firebase Authentication (Google OAuth)
2. **Backend**: Firebase ID token validation → API key generation
3. **Client**: API key-based authentication
4. **Machine Identification**: Unique machine ID generation using hostname + MAC address

### Security Measures
- Rate limiting on API endpoints
- CORS protection
- API key-based client authentication
- Firebase authentication for web users
- Input validation and sanitization
- Secure WebSocket connections

## Database Design

### MongoDB Collections
- **users**: User accounts and API keys
- **client_machines**: Registered client machines
- **task_executions**: Task execution records and history

### Indexes
- `users.firebase_uid` (unique)
- `users.api_key` (unique)
- `client_machines.machine_id` (unique)
- `task_executions.user_id`
- `task_executions.machine_id`

## Communication Protocols

### REST API Endpoints
- `POST /api/auth/login` - User authentication
- `POST /api/tasks` - Create new task
- `GET /api/tasks/list` - List user tasks
- `GET /api/tasks/status/{task_id}` - Get task status
- `GET /api/clients/list` - List user's client machines
- `POST /api/clients/register` - Register new client

### WebSocket Channels
- `/ws/frontend` - Frontend real-time updates
- `/ws/client` - Client agent communication

### Message Types
- `execute_command` - Command execution request
- `command_result` - Command execution result
- `task_status_update` - Task progress updates
- `client_log` - Client logging messages
- `heartbeat` - Connection keep-alive

## AI Integration

### LLM Service Architecture
- **Provider**: Google Gemini 2.0 Flash
- **Framework**: LangChain for prompt management
- **Temperature**: 0.1 (low creativity for accuracy)

### AI Capabilities
1. **Task Decomposition**: Break complex requests into Linux commands
2. **Output Validation**: Validate command results and suggest fixes
3. **Alternative Generation**: Generate alternative commands on failure
4. **Hanging Analysis**: Analyze stuck processes and recommend actions
5. **Summary Generation**: Generate AI summaries of completed tasks

## Deployment Architecture

### Development Environment
- Backend: `uvicorn` with hot reload
- Frontend: `vite` dev server with HMR
- Database: Local MongoDB instance
- Client: Direct Python execution

### Production Considerations
- Backend: ASGI server (Gunicorn + Uvicorn workers)
- Frontend: Static file serving (Nginx)
- Database: MongoDB Atlas or self-hosted cluster
- Client: System service deployment
- Load balancing for multiple backend instances
- SSL/TLS termination

## Scalability Considerations

### Horizontal Scaling
- Stateless backend design enables multiple instances
- MongoDB supports sharding for large datasets
- WebSocket connections can be load balanced

### Performance Optimizations
- Connection pooling for database operations
- Async/await for non-blocking operations
- WebSocket connection management
- Client heartbeat mechanisms

### Monitoring and Observability
- Structured logging throughout the system
- Real-time client status monitoring
- Task execution metrics
- Error tracking and alerting capabilities

## Technology Stack Summary

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Backend** | FastAPI + Python 3.12 | REST API and WebSocket server |
| **Database** | MongoDB + Motor | Data persistence with async operations |
| **Authentication** | Firebase Admin SDK | User authentication and authorization |
| **AI/LLM** | Google Gemini + LangChain | Task decomposition and validation |
| **Frontend** | Vue.js 3 + TypeScript | User interface and state management |
| **UI Framework** | Tailwind CSS + Headless UI | Responsive design system |
| **Build Tools** | Vite | Frontend build and development server |
| **Client Runtime** | Python 3.12 | Cross-platform client agent |
| **Real-time Communication** | WebSockets | Bidirectional client-server communication |
| **Process Management** | asyncio + subprocess | Async command execution |

## Conclusion

The AI Linux Agent employs a modern, scalable architecture that separates concerns while maintaining tight integration between components. The event-driven design ensures responsiveness, while the AI integration provides intelligent task decomposition and validation. The system is designed for both ease of development and production scalability.