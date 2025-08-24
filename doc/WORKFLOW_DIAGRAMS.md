# AI Linux Agent - Workflow Diagrams & Flow Charts

## 🔄 **Core System Workflows**

### **1. Complete User Journey Flow**

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Firebase
    participant Backend
    participant MongoDB
    participant Gemini
    participant Client
    participant Linux

    User->>Frontend: Access Dashboard
    Frontend->>Firebase: Authenticate User
    Firebase-->>Frontend: ID Token
    Frontend->>Backend: Login with Token
    Backend->>Firebase: Verify Token
    Backend->>MongoDB: Store/Update User
    Backend-->>Frontend: API Key
    Frontend->>Backend: WebSocket Connect
    
    Note over User,Linux: Command Execution Flow
    User->>Frontend: Enter Command
    Frontend->>Backend: POST /api/tasks
    Backend->>Gemini: Decompose Task
    Gemini-->>Backend: Subtasks Array
    Backend->>MongoDB: Store Task
    Backend->>Client: WebSocket Execute Command
    Client->>Linux: Execute Command
    Linux-->>Client: Output Stream
    Client-->>Frontend: Live Output
    Client-->>Backend: Command Result
    Backend->>Gemini: Validate Result
    Backend->>MongoDB: Update Task
    Backend-->>Frontend: Task Complete
```

### **2. Client Registration & Management Flow**

```mermaid
flowchart TD
    A[Python Client Startup] --> B[Load Environment Variables]
    B --> C[Generate/Load Machine ID]
    C --> D[Collect System Information]
    D --> E[HTTP POST /api/clients/register]
    E --> F{Registration Successful?}
    F -->|No| G[Log Error & Retry]
    F -->|Yes| H[Establish WebSocket Connection]
    H --> I[Send Initial System Info]
    I --> J[Start Heartbeat Loop]
    J --> K[Listen for Commands]
    K --> L{Command Received?}
    L -->|Yes| M[Execute Command with Monitoring]
    L -->|No| N[Continue Listening]
    M --> O[Stream Output to Server]
    O --> P[Send Result to Server]
    P --> N
    N --> Q{Connection Lost?}
    Q -->|Yes| R[Attempt Reconnection]
    Q -->|No| K
    R --> H
    G --> S[Wait 30 seconds]
    S --> E
```

### **3. AI-Powered Task Decomposition Flow**

```mermaid
flowchart TD
    A[User Input: 'Install and configure nginx'] --> B[LLM Task Decomposition Service]
    B --> C{Complex Task?}
    C -->|Simple| D[Single Command Task]
    C -->|Complex| E[Multi-Step Breakdown]
    
    E --> F[Step 1: Check if nginx installed]
    E --> G[Step 2: Install nginx if needed]
    E --> H[Step 3: Configure nginx]
    E --> I[Step 4: Start nginx service]
    E --> J[Step 5: Verify installation]
    
    F --> K[which nginx]
    G --> L[apt update && apt install nginx]
    H --> M[nginx -t && systemctl enable nginx]
    I --> N[systemctl start nginx]
    J --> O[systemctl status nginx]
    
    D --> P[Store in MongoDB]
    K --> P
    L --> P
    M --> P
    N --> P
    O --> P
    
    P --> Q[Send to Target Client]
    Q --> R[Execute with Smart Monitoring]
    R --> S[AI Validation of Results]
    S --> T[Generate Final Summary]
```

### **4. Smart Command Monitoring & Recovery Flow**

```mermaid
stateDiagram-v2
    [*] --> CommandStart: Execute Command
    CommandStart --> Monitoring: Start Process Monitor
    
    Monitoring --> Healthy: Output + CPU Activity
    Monitoring --> Idle: No Output, CPU Active
    Monitoring --> Hanging: No Output, No CPU
    Monitoring --> WaitingInput: Interactive Prompt
    Monitoring --> ErrorLoop: Repeating Errors
    
    Healthy --> Monitoring: Continue Monitoring
    Idle --> IdleTimeout: Wait 30-60s
    IdleTimeout --> Hanging: Still No Activity
    IdleTimeout --> Healthy: Activity Resumed
    
    Hanging --> GenerateAlternative: AI Alternative Generation
    ErrorLoop --> GenerateAlternative: AI Alternative Generation
    WaitingInput --> HandleInteractive: Prompt User Input
    
    GenerateAlternative --> ExecuteAlternative: Try Alternative Command
    ExecuteAlternative --> Monitoring: Monitor Alternative
    ExecuteAlternative --> Failed: All Alternatives Failed
    
    HandleInteractive --> Monitoring: Continue with Input
    
    Healthy --> Success: Command Completed (Exit Code 0)
    Success --> [*]: Report Success
    Failed --> [*]: Report Failure
```

### **5. Real-time WebSocket Communication Flow**

```mermaid
sequenceDiagram
    participant Frontend
    participant Backend
    participant WSManager
    participant Client1
    participant Client2
    
    Note over Frontend,Client2: Connection Establishment
    Frontend->>Backend: WebSocket Connect (Dashboard)
    Client1->>Backend: WebSocket Connect (Client)
    Client2->>Backend: WebSocket Connect (Client)
    Backend->>WSManager: Register Connections
    
    Note over Frontend,Client2: Command Distribution
    Frontend->>Backend: Execute Task on Client1
    Backend->>WSManager: Route to Client1
    WSManager->>Client1: Execute Command
    
    Note over Frontend,Client2: Live Output Streaming
    Client1->>WSManager: Live Output Stream
    WSManager->>Frontend: Forward Live Output
    WSManager->>Backend: Store Output
    
    Note over Frontend,Client2: Health Monitoring
    Client1->>WSManager: Health Update
    WSManager->>Frontend: Health Status
    WSManager->>Backend: Log Health Data
    
    Note over Frontend,Client2: Alternative Command Trigger
    Client1->>WSManager: Command Hanging Detected
    WSManager->>Backend: Generate Alternative
    Backend->>WSManager: Alternative Command
    WSManager->>Client1: Execute Alternative
    
    Note over Frontend,Client2: Task Completion
    Client1->>WSManager: Command Complete
    WSManager->>Backend: Update Task Status
    Backend->>WSManager: AI Summary Generated
    WSManager->>Frontend: Task Complete + Summary
```

## 📊 **Data Flow Architecture Diagrams**

### **6. Complete Data Architecture**

```mermaid
erDiagram
    Users ||--o{ Tasks : creates
    Users ||--o{ ClientMachines : owns
    Tasks ||--o{ SubTasks : contains
    SubTasks ||--o{ Attempts : has
    ClientMachines ||--o{ SystemInfo : reports
    Tasks ||--o{ AlternativeAttempts : may_have
    
    Users {
        string id PK
        string firebase_uid UK
        string email
        string api_key UK
        datetime created_at
        array client_machines FK
    }
    
    Tasks {
        string task_id PK
        string user_id FK
        string machine_id FK
        string original_prompt
        array subtasks
        int current_subtask_index
        string status
        datetime created_at
        datetime completed_at
        string ai_summary
    }
    
    SubTasks {
        string id PK
        string description
        string command
        string expected_output
        array dependencies
        array attempts
    }
    
    Attempts {
        int attempt_number
        string command
        string output
        int exit_code
        object validation_result
        datetime timestamp
    }
    
    ClientMachines {
        string machine_id PK
        string hostname
        string os_info
        string architecture
        string mac_address
        datetime last_seen
        boolean is_active
    }
    
    AlternativeAttempts {
        string original_command
        string alternative_command
        string reason
        int attempt_number
        object result
        datetime timestamp
    }
```

### **7. Security & Authentication Flow**

```mermaid
flowchart TD
    A[User Access Request] --> B{Authenticated?}
    B -->|No| C[Redirect to Login]
    C --> D[Firebase Authentication]
    D --> E[Google/Email Login]
    E --> F[Firebase ID Token]
    F --> G[Send to Backend]
    G --> H[Verify with Firebase Admin]
    H --> I{Valid Token?}
    I -->|No| J[Return 401 Unauthorized]
    I -->|Yes| K[Generate/Retrieve API Key]
    K --> L[Store User Session]
    L --> M[Return API Key to Frontend]
    M --> N[Store in Auth Store]
    N --> O[WebSocket Connection with API Key]
    O --> P[Authenticated Session Active]
    
    B -->|Yes| Q[Check API Key Validity]
    Q --> R{Valid API Key?}
    R -->|No| C
    R -->|Yes| P
    
    P --> S[Request to Protected Endpoint]
    S --> T[Extract API Key from Header]
    T --> U{API Key Valid?}
    U -->|No| J
    U -->|Yes| V[Process Request]
    V --> W[Return Response]
```

### **8. Command Safety & Validation Pipeline**

```mermaid
flowchart TD
    A[User Command Input] --> B[Input Sanitization]
    B --> C[Command Classification]
    C --> D{Dangerous Command?}
    D -->|Yes| E[Block Command]
    E --> F[Return Security Warning]
    D -->|No| G[Rate Limit Check]
    G --> H{Rate Exceeded?}
    H -->|Yes| I[Return Rate Limit Error]
    H -->|No| J[Parameter Validation]
    J --> K{Valid Parameters?}
    K -->|No| L[Return Validation Error]
    K -->|Yes| M[AI Task Decomposition]
    M --> N[Generate Subtask Commands]
    N --> O[Validate Each Subtask]
    O --> P{All Subtasks Safe?}
    P -->|No| Q[Block Unsafe Subtasks]
    P -->|Yes| R[Proceed to Execution]
    R --> S[Execute on Target Client]
    S --> T[Monitor Execution Safety]
    T --> U[AI Result Validation]
    U --> V[Return Results]
```

## 🚀 **Advanced Workflow Scenarios**

### **9. Multi-Client Task Orchestration**

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend
    participant Client1
    participant Client2
    participant Client3
    
    User->>Frontend: Deploy app to 3 servers
    Frontend->>Backend: Create orchestrated task
    Backend->>Backend: Decompose into parallel subtasks
    
    par Deploy to Client1
        Backend->>Client1: git pull && docker build
        Client1-->>Backend: Build progress
    and Deploy to Client2
        Backend->>Client2: git pull && docker build
        Client2-->>Backend: Build progress
    and Deploy to Client3
        Backend->>Client3: git pull && docker build
        Client3-->>Backend: Build progress
    end
    
    Note over Backend: Wait for all builds to complete
    
    par Start Services
        Backend->>Client1: docker-compose up -d
        Client1-->>Backend: Service started
    and Start Services
        Backend->>Client2: docker-compose up -d
        Client2-->>Backend: Service started
    and Start Services
        Backend->>Client3: docker-compose up -d
        Client3-->>Backend: Service started
    end
    
    Backend->>Backend: Generate deployment summary
    Backend-->>Frontend: All deployments complete
    Frontend-->>User: Success notification
```

### **10. Error Handling & Recovery Workflow**

```mermaid
flowchart TD
    A[Command Execution] --> B{Command Succeeds?}
    B -->|Yes| C[AI Validation]
    C --> D{AI Validates Success?}
    D -->|Yes| E[Mark as Successful]
    D -->|No| F[Generate Alternative]
    
    B -->|No| G{Exit Code Analysis}
    G --> H{Retryable Error?}
    H -->|Yes| I{Attempts < 3?}
    I -->|Yes| J[Retry with Delay]
    I -->|No| K[Generate Alternative]
    H -->|No| K
    
    J --> L[Execute Retry]
    L --> B
    
    F --> M[AI Alternative Generation]
    K --> M
    M --> N[Execute Alternative Command]
    N --> O{Alternative Succeeds?}
    O -->|Yes| P[Mark as Recovered]
    O -->|No| Q{More Alternatives?}
    Q -->|Yes| R[Try Next Alternative]
    Q -->|No| S[Mark as Failed]
    
    R --> N
    E --> T[Continue to Next Subtask]
    P --> T
    S --> U[Generate Failure Report]
    T --> V{More Subtasks?}
    V -->|Yes| W[Execute Next Subtask]
    V -->|No| X[Generate AI Summary]
    W --> A
```

### **11. Interactive Command Handling Flow**

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend
    participant Client
    participant Process
    
    User->>Frontend: sudo apt install package
    Frontend->>Backend: Execute interactive command
    Backend->>Client: Execute with interactive flag
    Client->>Process: Start subprocess
    Process-->>Client: Password prompt output
    Client->>Backend: Interactive prompt detected
    Backend->>Frontend: Prompt for user input
    Frontend-->>User: Show password prompt
    User->>Frontend: Enter password
    Frontend->>Backend: Send user input
    Backend->>Client: Forward user input
    Client->>Process: Send input to stdin
    Process-->>Client: Continue execution
    Client->>Backend: Stream remaining output
    Backend->>Frontend: Forward output
    Process-->>Client: Command complete
    Client->>Backend: Send final result
    Backend->>Frontend: Task complete
```

### **12. System Health Monitoring & Alerting**

```mermaid
stateDiagram-v2
    [*] --> Monitoring: System Start
    
    Monitoring --> Healthy: All Metrics Normal
    Monitoring --> Warning: Some Metrics Elevated
    Monitoring --> Critical: Metrics Exceed Thresholds
    
    Healthy --> Monitoring: Continuous Check
    Warning --> AlertUser: Send Warning
    Critical --> AlertUser: Send Critical Alert
    
    AlertUser --> WaitResponse: User Notified
    WaitResponse --> UserAction: User Takes Action
    WaitResponse --> AutoRecover: Timeout Reached
    
    UserAction --> Monitoring: Action Completed
    AutoRecover --> AttemptFix: Try Automatic Fix
    
    AttemptFix --> Monitoring: Fix Successful
    AttemptFix --> Escalate: Fix Failed
    
    Escalate --> [*]: Require Manual Intervention
    
    note right of Monitoring
        Monitor:
        - CPU Usage
        - Memory Usage
        - Disk Space
        - Network Connectivity
        - Process Health
        - Command Success Rate
    end note
```

These workflow diagrams provide a comprehensive view of how your AI Linux Agent system operates, from high-level user interactions down to detailed technical processes. Each diagram illustrates the sophisticated coordination between components that makes your system both powerful and reliable.