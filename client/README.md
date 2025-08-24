# AI Linux Agent - Client

Python client that runs on Linux machines to execute commands remotely through the AI Linux Agent system.

## Features

- **Secure Authentication**: Uses API key from backend
- **System Information Collection**: Automatically gathers and reports system details
- **Command Execution**: Safely executes commands with security checks
- **Real-time Communication**: WebSocket connection for live updates
- **Cross-platform**: Works on any Linux distribution
- **Docker Support**: Can run in Docker containers

## Installation

1. **Install Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. **Get API Key**:
   - Log in to the web dashboard with Firebase
   - Copy your API key from the dashboard
   - Set it in `.env` or pass as argument

## Usage

### Basic Usage
```bash
python run_client.py --api-key YOUR_API_KEY
```

### With Custom Server
```bash
python run_client.py --api-key YOUR_API_KEY --server-url ws://your-server:8000
```

### Using Environment Variables
```bash
export API_KEY=your_api_key_here
export SERVER_URL=ws://your-server:8000
python run_client.py
```

### Docker Usage
```bash
# Build image
docker build -t ai-linux-client .

# Run container
docker run -e API_KEY=your_api_key_here ai-linux-client
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `API_KEY` | API key from backend (required) | - |
| `SERVER_URL` | WebSocket server URL | `ws://localhost:8000` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `HEARTBEAT_INTERVAL` | Heartbeat interval in seconds | `30` |

### Command Line Options

```bash
python run_client.py --help
```

## Security Features

The client includes several security measures:

- **Command Validation**: Blocks potentially dangerous commands
- **Process Isolation**: Commands run in separate process groups
- **Timeout Protection**: Commands have execution timeouts
- **Safe Execution**: No system-critical operations allowed

### Blocked Command Patterns

- System destruction: `rm -rf /`, `mkfs.*`
- System modifications: `chmod 777 /`, `chown root /`
- System control: `shutdown`, `reboot`, `halt`
- User management: `userdel`, `sudo passwd`
- Critical file access: `/etc/passwd`, `/etc/shadow`

## System Information

The client automatically collects and reports:

- OS and kernel information
- Hardware details (CPU, memory, disk)
- Network interfaces
- System uptime and load
- Installed packages (when available)

## Troubleshooting

### Connection Issues
```bash
# Check network connectivity
ping your-server-hostname

# Test WebSocket connection
wscat -c ws://your-server:8000/ws/client
```

### Authentication Issues
- Verify API key is correct
- Check if user exists in backend database
- Ensure client is registered with the user

### Command Execution Issues
- Check command syntax
- Verify file permissions
- Review security restrictions
- Check system resources

## Logs

Client logs include:
- Connection status
- Command execution details
- Error messages
- System information updates

Set `LOG_LEVEL=DEBUG` for detailed logging.

## Development

### Project Structure
```
client/
├── src/
│   ├── client.py           # Main client logic
│   ├── system_info.py      # System information collector
│   ├── command_executor.py # Command execution engine
│   └── __init__.py
├── run_client.py           # Client runner script
├── requirements.txt        # Python dependencies
├── .env.example           # Environment configuration
└── README.md              # This file
```

### Running in Development
```bash
# Install development dependencies
pip install -r requirements.txt

# Run with debug logging
python run_client.py --log-level DEBUG --api-key YOUR_KEY
```