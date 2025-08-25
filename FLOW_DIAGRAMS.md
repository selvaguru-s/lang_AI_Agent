# AI Linux Agent - Flow Diagrams

## Overview

This document contains ASCII flow diagrams illustrating the key processes and data flows within the AI Linux Agent system. These diagrams provide visual representations of the workflows documented in the system architecture.

## 1. System Overview Diagram

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│                 │    │                 │    │                 │
│   Frontend      │    │   Backend       │    │   Client        │
│   (Vue.js)      │◄──►│   (FastAPI)     │◄──►│   Agent         │
│                 │    │                 │    │   (Python)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│                 │    │                 │    │                 │
│   Browser       │    │   MongoDB       │    │   Linux         │
│   Storage       │    │   Database      │    │   Commands      │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │
         │                       │
         └───────────────────────┘
                  │
                  ▼
         ┌─────────────────┐
         │                 │
         │   Firebase      │
         │   Auth          │
         │                 │
         └─────────────────┘
                  │
                  ▼
         ┌─────────────────┐
         │                 │
         │   Google        │
         │   Gemini AI     │
         │                 │
         └─────────────────┘
```

## 2. User Authentication Flow

```
┌─────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  User   │────►│Frontend  │────►│Firebase  │────►│Backend   │────►│Database  │
└─────────┘     └──────────┘     └──────────┘     └──────────┘     └──────────┘
     │               │                │                │                │
     │ 1.Click       │ 2.Auth         │ 3.ID Token     │ 4.Validate     │ 5.Store
     │ Login         │ Request        │ Return         │ Token          │ User
     │               │                │                │                │
     │               ▼                ▼                ▼                ▼
     │          ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
     │          │Google    │────►│JWT       │────►│API Key   │────►│WebSocket │
     │          │OAuth     │     │Token     │     │Generate  │     │Connect   │
     │          └──────────┘     └──────────┘     └──────────┘     └──────────┘
     │               │                │                │                │
     └───────────────┼────────────────┼────────────────┼────────────────┘
                     │                │                │
                 6.Success        7.Store           8.Authenticated
                  Response        Locally            Session
```

## 3. Task Creation and Execution Flow

```
User Input: "Install Docker on my server"
│
▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        TASK CREATION FLOW                              │
└─────────────────────────────────────────────────────────────────────────┘
│
├─► Frontend: Capture user prompt + selected machine
│   │
│   ▼
├─► Backend: Receive task creation request
│   │
│   ├─► Validate user permissions for target machine
│   │   │
│   │   ▼
│   ├─► Call LLM Service for task decomposition
│   │   │
│   │   ├─► Google Gemini: "Break down 'Install Docker' into Linux commands"
│   │   │   │
│   │   │   ▼
│   │   │   Response: [
│   │   │     {id: "1", command: "which docker", desc: "Check if already installed"},
│   │   │     {id: "2", command: "apt update", desc: "Update package lists"},
│   │   │     {id: "3", command: "apt install -y docker.io", desc: "Install Docker"},
│   │   │     {id: "4", command: "systemctl enable docker", desc: "Enable service"},
│   │   │     {id: "5", command: "systemctl start docker", desc: "Start service"}
│   │   │   ]
│   │   │
│   │   ▼
│   ├─► Create TaskExecution record in database
│   │
│   ▼
├─► Start task execution on target client
    │
    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       TASK EXECUTION FLOW                              │
└─────────────────────────────────────────────────────────────────────────┘
│
├─► Backend sends execute_command to Client via WebSocket
│   │
│   ▼
├─► Client receives and executes: "which docker"
│   │
│   ├─► subprocess.run("which docker")
│   │   │
│   │   ▼
│   ├─► Result: exit_code=1, output="/usr/bin/which: no docker in ..."
│   │
│   ▼
├─► Client sends command_result back to Backend
│   │
│   ▼
├─► Backend validates result with LLM Service
│   │
│   ├─► LLM Analysis: "Exit code 1 is valid - Docker not found"
│   │   │
│   │   ▼
│   ├─► Validation: {is_valid: true, should_retry: false}
│   │
│   ▼
├─► Backend proceeds to next subtask: "apt update"
│   │
│   ▼ (Process repeats for each subtask)
├─► Final Result: Task completed successfully
    │
    ▼
├─► Backend generates AI summary
    │
    ▼
└─► Frontend displays completion with summary
```

## 4. Client Registration and Heartbeat Flow

```
┌─────────────────┐
│ Client Startup  │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│Generate/Load    │
│Machine ID       │
│(hostname+MAC)   │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│Connect to       │
│Backend via      │
│WebSocket        │
└─────────────────┘
         │
         ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│Send System      │───►│Backend          │───►│Store Client     │
│Info Update      │    │Validates &      │    │Info in DB      │
│                 │    │Registers        │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│Start Heartbeat  │    │Mark Client      │    │Associate with   │
│Loop (30s)       │    │as Active        │    │User Account     │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │
         ▼
    ┌──────────┐
    │Every 30s:│
    └──────────┘
         │
    ┌────▼─────┐     ┌─────────────────┐     ┌─────────────────┐
    │Send      │────►│Backend Updates  │────►│Update last_seen │
    │Heartbeat │     │Client Status    │     │Timestamp        │
    └──────────┘     └─────────────────┘     └─────────────────┘
         │
         ▼
    ┌──────────┐
    │Ready for │
    │Commands  │
    └──────────┘
```

## 5. WebSocket Communication Flow

```
┌─────────────────┐              ┌─────────────────┐              ┌─────────────────┐
│    Frontend     │              │    Backend      │              │    Client       │
│   (Browser)     │              │   (FastAPI)     │              │   (Machine)     │
└─────────────────┘              └─────────────────┘              └─────────────────┘
         │                                │                                │
         │ 1. Connect with API key        │                                │
         ├────────────────────────────────►                                │
         │                                │ 2. Validate & establish        │
         ◄────────────────────────────────┤    connection                  │
         │                                │                                │
         │                                │ 3. Client connects with        │
         │                                │    API key + machine_id        │
         │                                ◄────────────────────────────────┤
         │                                │                                │
         │                                │ 4. Validate & register         │
         │                                ├────────────────────────────────►
         │                                │                                │
         │ 5. User creates task           │                                │
         ├────────────────────────────────►                                │
         │                                │                                │
         │                                │ 6. Send execute_command        │
         │                                ├────────────────────────────────►
         │                                │                                │
         │                                │ 7. Execute and send result     │
         │                                ◄────────────────────────────────┤
         │                                │                                │
         │ 8. Broadcast status update     │                                │
         ◄────────────────────────────────┤                                │
         │                                │                                │
         │                                │ 9. Heartbeat every 30s        │
         │                                ◄────────────────────────────────┤
         │                                │                                │

Message Types:
Frontend ↔ Backend:
- task_status_update
- client_status_update  
- ai_summary_update

Backend ↔ Client:
- execute_command
- command_result
- system_info_update
- heartbeat
- client_log
```

## 6. Error Handling and Retry Flow

```
┌─────────────────┐
│Command Execution│
│Starts           │
└─────────────────┘
         │
         ▼
┌─────────────────┐    Success     ┌─────────────────┐
│Execute Linux    │───────────────►│Command          │
│Command          │                │Completed        │
└─────────────────┘                └─────────────────┘
         │                                  │
      Failure                               ▼
         │                        ┌─────────────────┐
         ▼                        │Next Subtask     │
┌─────────────────┐               │or Task Complete │
│Send Result to   │               └─────────────────┘
│Backend          │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│LLM Validates    │
│Output           │
└─────────────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌─────────┐ ┌─────────┐
│Valid    │ │Invalid  │
│Failure  │ │Failure  │
└─────────┘ └─────────┘
    │         │
    │         ▼
    │    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
    │    │LLM Generates    │───►│Retry < 3 times? │───►│Execute Alt      │
    │    │Alternative      │    │                 │    │Command          │
    │    │Command          │    └─────────────────┘    └─────────────────┘
    │    └─────────────────┘            │                       │
    │                                   │ No                    │
    │                                   ▼                       ▼
    │                          ┌─────────────────┐    ┌─────────────────┐
    │                          │Mark Subtask     │    │Back to Execute  │
    │                          │Failed           │    │Command          │
    │                          └─────────────────┘    └─────────────────┘
    │                                   │
    └───────────────────────────────────┼─────────────────────────────────┐
                                        ▼                                 │
                               ┌─────────────────┐                       │
                               │Continue Next    │◄──────────────────────┘
                               │Subtask or End   │
                               │Task             │
                               └─────────────────┘
```

## 7. Database Schema Relationships

```
┌─────────────────────────────────┐
│            Users               │
├─────────────────────────────────┤
│ _id: ObjectId (PK)             │
│ firebase_uid: String (Unique)  │
│ email: String                  │
│ name: String                   │
│ api_key: String (Unique)       │
│ created_at: DateTime           │
│ last_login: DateTime           │
│ is_active: Boolean             │
│ client_machines: [String]      │
└─────────────────────────────────┘
         │ 1:N
         │
         ▼
┌─────────────────────────────────┐
│        Client Machines         │
├─────────────────────────────────┤
│ _id: ObjectId (PK)             │
│ machine_id: String (Unique)    │
│ hostname: String               │
│ os_info: String                │
│ architecture: String           │
│ mac_address: String            │
│ last_seen: DateTime            │
│ is_active: Boolean             │
└─────────────────────────────────┘
         │ 1:N
         │
         ▼
┌─────────────────────────────────┐
│        Task Executions         │
├─────────────────────────────────┤
│ task_id: String (PK)           │
│ user_id: String (FK)           │
│ machine_id: String (FK)        │
│ original_prompt: String        │
│ subtasks: [SubTask]            │
│ current_subtask_index: Number  │
│ status: String                 │
│ created_at: DateTime           │
│ completed_at: DateTime         │
│ error_message: String          │
│ ai_summary: String             │
└─────────────────────────────────┘
         │ 1:N
         │
         ▼
┌─────────────────────────────────┐
│          SubTasks              │
├─────────────────────────────────┤
│ id: String                     │
│ description: String            │
│ command: String                │
│ expected_output: String        │
│ status: String                 │
│ attempts: [SubtaskAttempt]     │
│ dependencies: [String]         │
└─────────────────────────────────┘
         │ 1:N
         │
         ▼
┌─────────────────────────────────┐
│       SubTask Attempts         │
├─────────────────────────────────┤
│ attempt_number: Number         │
│ command: String                │
│ output: String                 │
│ exit_code: Number              │
│ validation_result: Object      │
│ timestamp: DateTime            │
└─────────────────────────────────┘
```

## 8. AI Integration Flow

```
┌─────────────────┐
│User Natural     │
│Language Prompt  │
│"Install nginx"  │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│Backend receives │
│task creation    │
│request          │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│Call LLM Service │
│decompose_task() │
└─────────────────┘
         │
         ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│Build system     │───►│Send to Google   │───►│Receive JSON     │
│context prompt   │    │Gemini API       │    │response         │
│with OS info     │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│System: Ubuntu   │    │Prompt: "Break   │    │Response:        │
│Arch: x86_64     │    │'Install nginx'  │    │[{id:"1",        │
│Hostname: web01  │    │into Linux       │    │cmd:"which nginx"│
│                 │    │commands..."     │    │desc:"Check..."}]│
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
                                                       ▼
                                              ┌─────────────────┐
                                              │Parse JSON and   │
                                              │create SubTask   │
                                              │objects          │
                                              └─────────────────┘
                                                       │
                                              After execution:
                                                       │
                                                       ▼
                                              ┌─────────────────┐
                                              │Call LLM         │
                                              │generate_summary │
                                              │with all results │
                                              └─────────────────┘
                                                       │
                                                       ▼
                                              ┌─────────────────┐
                                              │AI Summary:      │
                                              │"Successfully    │
                                              │installed nginx  │
                                              │web server..."   │
                                              └─────────────────┘
```

These flow diagrams provide a comprehensive visual guide to understanding how the AI Linux Agent system operates, from high-level architecture down to specific process flows. They can be used for system documentation, onboarding new developers, and troubleshooting system issues.