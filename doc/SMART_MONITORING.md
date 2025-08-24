# Intelligent Command Monitoring System

## Overview

The AI Linux Agent now includes an intelligent command monitoring system that can automatically detect hanging commands, analyze their health, and generate alternative commands when the original ones fail or get stuck.

## Key Features

### 🧠 Smart Command Classification
Commands are automatically classified into types for appropriate timeout handling:
- **Quick Info** (`ls`, `pwd`, `whoami`) - 10s/30s timeouts
- **Package Management** (`apt install`, `pip install`) - 60s/600s timeouts  
- **System Services** (`systemctl`, `service`) - 30s/120s timeouts
- **Network Operations** (`wget`, `curl`, `ssh`) - 45s/300s timeouts
- **File Operations** (`find`, `cp`, `chmod`) - 30s/300s timeouts
- **Compilation** (`make`, `gcc`, `npm build`) - 120s/1800s timeouts
- **Interactive** (`sudo`, `vim`, `mysql`) - 300s/1800s timeouts

### 🚨 Intelligent Hanging Detection
The system monitors multiple indicators:
- **Output Activity**: Time since last output
- **CPU Usage**: Process CPU utilization
- **Memory Growth**: Process memory consumption
- **Process State**: Whether process is actually working

### 🔄 Automatic Alternative Commands
When commands hang or fail, the system can:
- Generate alternative commands using AI
- Try different tools for the same purpose
- Suggest fallback approaches
- Learn from successful alternatives

### 📊 Real-time Health Monitoring
Process health is continuously monitored:
- `HEALTHY` - Normal operation with output/activity
- `IDLE` - No recent output but process active
- `HANGING` - No output, no CPU activity, likely stuck
- `WAITING_INPUT` - Waiting for user input
- `ERROR_LOOP` - Repeating same error messages

## Usage

### Basic Usage (Automatic)
The enhanced monitoring is enabled by default when using the AI Linux Agent. No configuration required!

### Manual Testing
```bash
# Test the monitoring system
python3 simple_monitoring_test.py

# Test with real hanging commands (manual)
python3 test_smart_monitoring.py --hanging-test
```

### Configuration Options
Timeout configurations can be customized in `smart_command_monitor.py`:

```python
TIMEOUT_CONFIGS = {
    CommandType.QUICK_INFO: TimeoutConfig(
        no_output_timeout=10,    # Alert after 10s of no output
        max_total_timeout=30,    # Kill after 30s total
        cpu_threshold=0.1,       # Consider hanging if CPU < 0.1%
        check_interval=1.0       # Check every 1 second
    )
}
```

## API Endpoints

The system adds new API endpoints for alternative command generation:

### Generate Alternative Commands
```http
POST /api/commands/generate-alternatives
Content-Type: application/json
Authorization: Bearer YOUR_API_KEY

{
    "original_command": "apt install nonexistent-package",
    "failure_reason": "Package not found",
    "system_info": {"os": "Linux", "arch": "x86_64"},
    "process_metrics": {
        "cpu_percent": 0.0,
        "memory_mb": 50.0,
        "total_output_size": 0
    }
}
```

### Analyze Hanging Commands
```http
POST /api/commands/analyze-hanging
Content-Type: application/json
Authorization: Bearer YOUR_API_KEY

{
    "command": "wget https://slow-server.com/large-file.zip",
    "output_so_far": "Connecting to slow-server.com...",
    "process_metrics": {
        "cpu_percent": 0.1,
        "memory_mb": 25.0,
        "last_output_time": 1634567890
    }
}
```

## WebSocket Messages

New WebSocket message types for real-time monitoring:

### Process Health Updates
```json
{
    "type": "process_health_update",
    "task_id": "task_123",
    "health_status": "hanging",
    "metrics": {
        "cpu_percent": 0.0,
        "memory_mb": 50.0,
        "last_output_time": 1634567890,
        "total_output_size": 1024,
        "is_interactive": false
    }
}
```

### Alternative Command Triggered
```json
{
    "type": "alternative_command_triggered",
    "task_id": "task_123",
    "original_command": "apt install broken-package",
    "alternative_command": "apt update && apt install broken-package",
    "reason": "Package lists might be outdated",
    "attempt_number": 1
}
```

### Alternative Command Result
```json
{
    "type": "alternative_command_result",
    "task_id": "task_123",
    "command": "apt update && apt install broken-package",
    "stdout": "Package installed successfully",
    "stderr": "",
    "exit_code": 0,
    "attempt_number": 1
}
```

## Implementation Details

### Architecture
```
┌─────────────────────────────────────────┐
│         Enhanced Command Executor       │
├─────────────────────────────────────────┤
│  ┌─────────────────┐ ┌─────────────────┐ │
│  │ Smart Command   │ │ Alternative     │ │
│  │ Monitor         │ │ Generator       │ │
│  │ - Classification│ │ - LLM Service   │ │
│  │ - Health Check  │ │ - Heuristics    │ │
│  │ - Timeout Logic │ │ - Pattern Match │ │
│  └─────────────────┘ └─────────────────┘ │
└─────────────────────────────────────────┘
                    │
                    ▼
           ┌─────────────────┐
           │ WebSocket       │
           │ Communication   │
           │ - Health Updates│
           │ - Alternatives  │
           │ - Results       │
           └─────────────────┘
```

### Key Components

1. **SmartCommandMonitor** (`smart_command_monitor.py`)
   - Command classification
   - Timeout configuration
   - Health monitoring
   - Hanging detection

2. **EnhancedCommandExecutor** (`enhanced_command_executor.py`)
   - Wraps existing executor
   - Integrates smart monitoring
   - Handles alternatives
   - Real-time communication

3. **LLM Service Extensions** (`llm_service.py`)
   - Alternative command generation
   - Hanging analysis
   - Heuristic fallbacks

4. **API Endpoints** (`commands.py`)
   - Alternative generation API
   - Hanging analysis API
   - Command pattern info

## Benefits

### For Users
- **Faster Problem Resolution**: Automatic alternatives when commands hang
- **Better Visibility**: Real-time process health information
- **Reduced Frustration**: No more waiting for hung commands
- **Learning System**: Improves over time with usage

### For System Administrators
- **Proactive Monitoring**: Early detection of problematic commands
- **Resource Efficiency**: Prevents resource waste from hung processes
- **Detailed Logging**: Comprehensive command execution history
- **Pattern Recognition**: Identify common failure scenarios

## Example Scenarios

### Scenario 1: Package Installation Timeout
```
Original: apt install large-package
Problem: Package repository is slow
Detection: No output for 60 seconds
Alternative: apt update && apt install large-package
Result: Success - updated package lists resolved the issue
```

### Scenario 2: Network Download Hanging
```
Original: wget https://slow-server.com/file.zip
Problem: Server not responding
Detection: No CPU activity, no output for 45 seconds
Alternative: curl -O https://slow-server.com/file.zip
Result: Success - curl handled the connection better
```

### Scenario 3: Service Status Check Failure
```
Original: systemctl status unknown-service
Problem: Service doesn't exist
Detection: Error loop detected
Alternative: ps aux | grep unknown-service
Result: Confirmation - service truly not running
```

## Future Enhancements

- **Learning Algorithms**: Improve alternative selection based on historical success
- **User Preferences**: Allow users to configure monitoring sensitivity
- **Integration Hooks**: Connect with external monitoring systems
- **Performance Optimization**: Reduce monitoring overhead for high-frequency commands
- **Command Templates**: Pre-defined alternatives for common scenarios

## Troubleshooting

### Common Issues

1. **False Positives**: Command marked as hanging when it's actually working
   - **Solution**: Adjust timeout configurations for specific command types
   - **Config**: Modify `TIMEOUT_CONFIGS` in `smart_command_monitor.py`

2. **Alternatives Not Generated**: No alternatives suggested for failed commands
   - **Check**: LLM service connectivity and API key
   - **Fallback**: Heuristic alternatives should still work

3. **High CPU Usage**: Monitoring consuming too many resources
   - **Solution**: Increase check intervals
   - **Config**: Adjust `check_interval` in timeout configurations

### Debug Mode
Enable detailed logging:
```python
import logging
logging.getLogger().setLevel(logging.DEBUG)
```

### Health Check
Verify system status:
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
     http://localhost:8000/api/commands/health-metrics
```

## Security Considerations

- **Command Validation**: All commands go through safety checks
- **Alternative Filtering**: Generated alternatives are validated for safety
- **Resource Limits**: Monitoring processes have CPU and memory limits
- **API Authentication**: All endpoints require valid API keys
- **Process Isolation**: Commands run in isolated process groups

The intelligent command monitoring system provides a significant enhancement to the AI Linux Agent, making it more reliable, efficient, and user-friendly for managing remote Linux systems.