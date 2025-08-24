# AI Linux Agent

A sophisticated distributed system for remote Linux command execution and monitoring through AI-powered task decomposition. This system allows users to manage multiple Linux machines remotely via a web dashboard, with intelligent command breakdown and execution validation.

## 🚀 Features

### Core Capabilities
- **AI-Powered Task Decomposition**: Uses Gemini 2.0 Flash to break down complex user requests into executable Linux commands
- **Real-time Monitoring**: Live WebSocket updates showing command execution progress
- **Multi-Machine Management**: Manage multiple Linux clients from a single dashboard
- **Intelligent Retry Logic**: 3-attempt retry mechanism with LLM validation for failed commands
- **Security-First Design**: Command validation, rate limiting, and secure authentication

### User Experience
- **Firebase Authentication**: Secure login with Google or email/password
- **Intuitive Dashboard**: Modern Vue.js interface with Tailwind CSS
- **Live Terminal**: Real-time command output and execution status
- **Client Management**: Register, monitor, and control multiple Linux machines
- **Task History**: Track all executed commands and their results

### Security Features
- **Command Validation**: Blocks dangerous operations (system destruction, unauthorized access)
- **Rate Limiting**: Prevents abuse with configurable request limits
- **Secure Communication**: End-to-end encrypted WebSocket connections
- **API Key Authentication**: Unique keys for each user with secure validation
- **Process Isolation**: Commands run in isolated environments with timeouts

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     AI Linux Agent System                      │
├─────────────────┬─────────────────┬─────────────────────────────┤
│   Vue.js        │   FastAPI       │   MongoDB                   │
│   Frontend      │   Backend       │   Database                  │
│   - Dashboard   │   - API Server  │   - User Management         │
│   - Auth UI     │   - WebSocket   │   - Client Registry         │
│   - Live Term   │   - LLM Integ   │   - Task History            │
└─────────────────┼─────────────────┼─────────────────────────────┘
                  │                 │
                  │ Real-time Communication
                  │
    ┌─────────────▼─────────────────────────────────────┐
    │              Python Clients                       │
    │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐  │
    │  │   Client 1  │ │   Client 2  │ │   Client N  │  │
    │  │ (Ubuntu)    │ │ (CentOS)    │ │ (Docker)    │  │
    │  │ - Exec Cmds │ │ - Exec Cmds │ │ - Exec Cmds │  │
    │  │ - Report    │ │ - Report    │ │ - Report    │  │
    │  │ - Monitor   │ │ - Monitor   │ │ - Monitor   │  │
    │  └─────────────┘ └─────────────┘ └─────────────┘  │
    └─────────────────────────────────────────────────┘
```

## 🛠️ Technology Stack

### Frontend
- **Vue.js 3**: Modern reactive framework with Composition API
- **Tailwind CSS**: Utility-first CSS framework for rapid styling
- **Pinia**: State management for Vue.js applications
- **Firebase SDK**: Authentication and user management
- **Axios**: HTTP client for API communication
- **WebSocket Client**: Real-time communication with backend

### Backend
- **FastAPI**: High-performance Python web framework
- **WebSockets**: Real-time bidirectional communication
- **MongoDB**: Document database with async operations
- **Firebase Admin**: Server-side authentication verification
- **Gemini 2.0 Flash**: Google's latest AI model for task decomposition
- **LangChain**: AI framework for structured LLM interactions
- **Pydantic**: Data validation and serialization

### Client
- **Python 3.8+**: Cross-platform compatibility
- **AsyncIO**: Asynchronous programming for efficient I/O
- **WebSocket Client**: Real-time server communication
- **psutil**: System information collection
- **subprocess**: Secure command execution with isolation

## 📁 Project Structure

```
ai-linux-agent/
├── frontend/                 # Vue.js Web Dashboard
│   ├── src/
│   │   ├── components/       # Reusable Vue components
│   │   ├── views/           # Page components
│   │   ├── stores/          # Pinia state management
│   │   ├── services/        # API and Firebase services
│   │   └── router/          # Vue Router configuration
│   ├── package.json
│   └── tailwind.config.js
│
├── backend/                  # FastAPI Server
│   ├── app/
│   │   ├── routers/         # API endpoints
│   │   └── middleware.py    # Security middleware
│   ├── config/              # Database and Firebase config
│   ├── models/              # Pydantic data models
│   ├── utils/               # Utilities and services
│   └── requirements.txt
│
├── client/                   # Python Agent
│   ├── src/
│   │   ├── client.py        # Main client application
│   │   ├── system_info.py   # System information collector
│   │   └── command_executor.py # Command execution engine
│   ├── requirements.txt
│   └── run_client.py        # Client runner script
│
├── DEPLOYMENT.md            # Production deployment guide
└── README.md               # This file
```

## 🚀 Quick Start

### Prerequisites
- **Python 3.8+** with pip
- **Node.js 18+** with npm
- **MongoDB 4.4+**
- **Firebase Project** with Authentication enabled
- **Google Cloud Account** with Gemini API access

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Firebase and Gemini credentials

# Run server
uvicorn app.main:app --reload
```

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Edit .env with your Firebase configuration

# Run development server
npm run dev
```

### 3. Client Setup

```bash
cd client

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Get API key from web dashboard after login

# Run client
python run_client.py --api-key YOUR_API_KEY
```

## 📖 Usage Guide

### 1. Authentication
1. Open the web dashboard (http://localhost:3000)
2. Sign up/login with Google or email/password
3. Obtain your unique API key from the dashboard

### 2. Client Registration
1. Run the Python client on your Linux machines
2. Use your API key for authentication
3. Clients appear automatically in the dashboard

### 3. Command Execution
1. Select a target machine from the dropdown
2. Enter your command or describe what you want to do
3. Watch real-time execution in the live terminal
4. View detailed results and validation feedback

### 4. Task Management
- Monitor running tasks in real-time
- View execution history and logs
- Cancel long-running operations
- Review command validation results

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
```bash
MONGODB_URL=mongodb://localhost:27017
FIREBASE_SERVICE_ACCOUNT_KEY={"type": "service_account", ...}
GEMINI_API_KEY=your_gemini_api_key
SECRET_KEY=your_secret_key
ALLOWED_ORIGINS=http://localhost:3000
```

#### Frontend (.env)
```bash
VITE_FIREBASE_API_KEY=your_firebase_api_key
VITE_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your-project-id
VITE_API_BASE_URL=http://localhost:8000/api
VITE_WS_URL=ws://localhost:8000
```

#### Client (.env)
```bash
API_KEY=your_api_key_from_dashboard
SERVER_URL=ws://localhost:8000
LOG_LEVEL=INFO
HEARTBEAT_INTERVAL=30
```

## 🔒 Security

### Built-in Security Features
- **Command Validation**: Automatically blocks dangerous commands
- **Rate Limiting**: Prevents API abuse
- **Input Sanitization**: Validates all user inputs
- **Secure Authentication**: Firebase + API key dual authentication
- **Process Isolation**: Commands run in separate process groups
- **Timeout Protection**: Automatic termination of long-running commands

### Command Restrictions
The system automatically blocks:
- System destruction commands (`rm -rf /`, `mkfs.*`)
- System control operations (`shutdown`, `reboot`)
- User management (`userdel`, `passwd root`)
- Critical file modifications (`/etc/passwd`, `/etc/shadow`)
- Network security bypasses (`iptables -F`, `ufw disable`)

## 📊 Monitoring

### Real-time Metrics
- Client connection status
- Command execution progress
- System resource usage
- Task completion rates
- Error frequencies

### Logging
- Structured JSON logs
- Request/response tracking
- Error monitoring
- Performance metrics

## 🚀 Deployment

For production deployment, see the comprehensive [DEPLOYMENT.md](DEPLOYMENT.md) guide which covers:
- Server provisioning and setup
- SSL certificate configuration
- Database security hardening
- Nginx configuration
- Docker deployment options
- Monitoring and alerting setup
- Backup strategies

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Documentation**: Check component-specific README files
- **Issues**: Open GitHub issues for bugs and feature requests
- **Security**: Report security vulnerabilities via private channels

## 🗺️ Roadmap

### Upcoming Features
- [ ] Multi-tenant support
- [ ] Advanced command scheduling
- [ ] File transfer capabilities
- [ ] Performance analytics dashboard
- [ ] Mobile app for monitoring
- [ ] Integration with CI/CD pipelines
- [ ] Plugin system for custom commands
- [ ] Advanced RBAC (Role-Based Access Control)

### Performance Improvements
- [ ] Command output streaming
- [ ] Connection pooling optimization
- [ ] Caching layer implementation
- [ ] Database sharding support

This AI Linux Agent provides a powerful, secure, and user-friendly solution for remote Linux management with the intelligence of modern AI assistance.