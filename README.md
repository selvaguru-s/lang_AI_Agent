# AI Linux Agent

A distributed system for remote Linux command execution powered by AI. The system enables users to execute complex Linux operations on remote machines using natural language prompts through an intuitive web interface.

## 🚀 Overview

The AI Linux Agent consists of three main components:
- **Backend API**: FastAPI-based server with AI integration
- **Frontend Web App**: Vue.js-based user interface
- **Client Agents**: Python-based agents running on target machines

Users can interact with remote Linux systems by typing natural language commands like "Install Docker" or "Check system status", which are automatically decomposed into appropriate Linux commands and executed safely.

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │◄──►│   Backend       │◄──►│   Client        │
│   (Vue.js)      │    │   (FastAPI)     │    │   Agent         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
    Browser                 MongoDB                 Linux
    Storage                Database                Commands
         │                       │                       │
         └─── Firebase Auth ─────┴─── Google Gemini ────┘
```

## 📁 Project Structure

```
ai-linux-agent/
├── backend/                    # FastAPI backend server
│   ├── app/
│   │   ├── main.py            # Application entry point
│   │   ├── middleware.py      # Security & logging middleware
│   │   └── routers/           # API route handlers
│   │       ├── auth.py        # Authentication endpoints
│   │       ├── clients.py     # Client management
│   │       ├── tasks.py       # Task execution
│   │       ├── commands.py    # Command handling
│   │       └── websocket.py   # Real-time communication
│   ├── config/
│   │   ├── database.py        # MongoDB configuration
│   │   └── firebase.py        # Firebase setup
│   ├── models/
│   │   └── user.py            # Database models
│   ├── utils/
│   │   ├── auth.py            # Authentication utilities
│   │   ├── llm_service.py     # AI/LLM integration
│   │   └── security.py        # Security utilities
│   └── requirements.txt       # Python dependencies
├── frontend/                   # Vue.js web application
│   ├── src/
│   │   ├── App.vue            # Root component
│   │   ├── components/        # Reusable components
│   │   ├── views/             # Page components
│   │   ├── router/            # Vue Router configuration
│   │   ├── stores/            # Pinia state management
│   │   └── services/          # API & WebSocket services
│   ├── public/                # Static assets
│   └── package.json           # Node.js dependencies
├── client/                     # Python client agent
│   ├── client.py              # Main client implementation
│   ├── run_client.py          # Client startup script
│   ├── config/                # Client configuration
│   └── requirements.txt       # Python dependencies
└── docs/                       # Documentation files
    ├── SYSTEM_ARCHITECTURE.md
    ├── WORKFLOW_AND_DATA_FLOW.md
    ├── TECH_STACK.md
    └── FLOW_DIAGRAMS.md
```

## 🛠️ Technology Stack

### Backend
- **FastAPI** (0.104.1) - High-performance web framework
- **MongoDB** + **Motor** - Async database operations  
- **Firebase Admin SDK** - Authentication
- **Google Gemini AI** + **LangChain** - Task decomposition & validation
- **WebSockets** - Real-time communication
- **Python 3.12+** - Modern Python features

### Frontend
- **Vue.js 3** - Progressive web framework
- **Pinia** - State management
- **Tailwind CSS** + **Headless UI** - Styling and components
- **Vite** - Build tool and dev server
- **Firebase SDK** - Client-side authentication
- **Axios** - HTTP client

### Client Agent
- **Python 3.12+** - Cross-platform compatibility
- **WebSockets** - Server communication
- **psutil** - System monitoring
- **asyncio** - Async operations

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Node.js 18+ 
- MongoDB (local or Atlas)
- Firebase project
- Google AI API key (Gemini)

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   Create `.env` file in backend directory:
   ```bash
   # Database
   MONGODB_URL=mongodb://localhost:27017

   # Authentication
   FIREBASE_PROJECT_ID=your-firebase-project-id
   
   # AI Service
   GEMINI_API_KEY=your-gemini-api-key
   
   # Server Configuration
   HOST=0.0.0.0
   PORT=8000
   ALLOWED_ORIGINS=http://localhost:3000
   ```

5. **Start the backend server:**
   ```bash
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Configure environment:**
   Create `.env` file in frontend directory:
   ```bash
   VITE_API_BASE_URL=http://localhost:8000/api
   VITE_WS_URL=ws://localhost:8000/ws
   
   # Firebase Configuration
   VITE_FIREBASE_API_KEY=your-firebase-api-key
   VITE_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
   VITE_FIREBASE_PROJECT_ID=your-project-id
   ```

4. **Start development server:**
   ```bash
   npm run dev
   ```

### Client Agent Setup

1. **Navigate to client directory:**
   ```bash
   cd client
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure client:**
   Create `.env` file in client directory:
   ```bash
   API_KEY=your-api-key-from-web-interface
   SERVER_URL=ws://localhost:8000
   HEARTBEAT_INTERVAL=30
   LOG_LEVEL=INFO
   ```

5. **Run the client:**
   ```bash
   python run_client.py
   ```

## 🔧 Configuration

### Firebase Setup
1. Create a Firebase project at https://console.firebase.google.com
2. Enable Authentication with Google provider
3. Generate service account key for backend
4. Get web app config for frontend

### Google AI Setup
1. Get API key from https://makersuite.google.com/app/apikey
2. Enable Gemini API access
3. Configure API key in backend environment

### MongoDB Setup
- **Local**: Install MongoDB Community Edition
- **Cloud**: Create MongoDB Atlas cluster
- Configure connection string in backend environment

## 📖 Usage

### Web Interface

1. **Login**: Visit the web interface and authenticate with Google
2. **Register Client**: Your API key will be displayed after login
3. **Create Tasks**: Use natural language to describe what you want to do:
   - "Install nginx on my server"
   - "Check disk space and memory usage"  
   - "Update all system packages"
   - "Create a backup of the home directory"

### Command Examples

The AI can handle various types of requests:

- **Installation**: "Install Docker and start the service"
- **System Monitoring**: "Check CPU usage and running processes"
- **File Operations**: "Create a backup of /home/user/documents"
- **Service Management**: "Restart nginx and check its status"
- **Network Diagnostics**: "Test connectivity to google.com"

### Task Monitoring

- View real-time execution progress
- See detailed command outputs
- Monitor multiple machines simultaneously
- Get AI-generated summaries of completed tasks

## 🔐 Security

### Authentication Flow
1. Frontend authenticates with Firebase (Google OAuth)
2. Backend validates Firebase ID tokens
3. API keys generated for client authentication
4. All communications secured with HTTPS/WSS

### Security Features
- Rate limiting on API endpoints
- Input validation and sanitization
- Secure WebSocket connections
- Machine-specific authentication
- User-based data isolation

## 🚀 Deployment

### Production Considerations

**Backend:**
- Use Gunicorn with Uvicorn workers for production
- Set up reverse proxy with Nginx
- Configure SSL/TLS certificates
- Use environment-based configuration

**Frontend:**
- Build with `npm run build`
- Serve static files with Nginx
- Configure CDN for assets
- Enable HTTPS

**Client:**
- Deploy as system service (systemd)
- Configure automatic startup
- Set up log rotation
- Monitor client connectivity

### Docker Deployment (Optional)

Create `docker-compose.yml` for containerized deployment:

```yaml
version: '3.8'
services:
  mongodb:
    image: mongo:latest
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - MONGODB_URL=mongodb://mongodb:27017
    depends_on:
      - mongodb

  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    depends_on:
      - backend

volumes:
  mongodb_data:
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 API Documentation

Once the backend is running, visit:
- **Interactive API Docs**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc

## 🔍 Monitoring & Debugging

### Logs
- **Backend**: Structured logging with Python logging module
- **Frontend**: Browser console and network tab
- **Client**: Detailed execution logs sent via WebSocket

### Health Checks
- Backend: `GET /health`
- WebSocket connections: Heartbeat monitoring
- Client status: Real-time connection monitoring

## ❓ Troubleshooting

### Common Issues

**Backend won't start:**
- Check MongoDB connection string
- Verify Firebase credentials
- Ensure all environment variables are set

**Client can't connect:**
- Verify API key is correct
- Check WebSocket URL configuration
- Ensure backend is running and accessible

**Tasks fail to execute:**
- Check client machine permissions
- Verify commands are appropriate for target OS
- Review client logs for execution details

### Debug Mode
Enable debug logging by setting `LOG_LEVEL=DEBUG` in environment variables.

## 📄 Documentation

For detailed documentation, see:
- [System Architecture](SYSTEM_ARCHITECTURE.md) - Detailed system design
- [Workflow & Data Flow](WORKFLOW_AND_DATA_FLOW.md) - Process flows
- [Technology Stack](TECH_STACK.md) - Complete tech stack details
- [Flow Diagrams](FLOW_DIAGRAMS.md) - Visual system diagrams

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues, questions, or contributions:
- Create an issue in the GitHub repository
- Check existing documentation
- Review logs for detailed error information

---

**Built with ❤️ using modern technologies for reliable, secure, and intelligent remote system management.**