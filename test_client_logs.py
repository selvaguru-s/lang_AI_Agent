#!/usr/bin/env python3
"""
Test Client Logs Integration

Tests that client-side logs are properly sent to backend and forwarded to frontend.
This verifies the complete flow from client -> backend -> frontend for detailed execution logs.
"""

import asyncio
import json
import websockets
import os
from datetime import datetime

async def test_client_logs():
    """Test sending client logs to backend"""
    
    # Configuration
    api_key = os.getenv("API_KEY", "test-api-key")  
    server_url = os.getenv("SERVER_URL", "ws://localhost:8000")
    machine_id = "test_machine_001"
    
    print("🧪 Testing Client Logs Integration")
    print("=" * 40)
    print(f"Server URL: {server_url}")
    print(f"Machine ID: {machine_id}")
    print()
    
    try:
        # Connect to client WebSocket endpoint
        client_uri = f"{server_url.replace('http', 'ws')}/ws/client?api_key={api_key}&machine_id={machine_id}"
        
        print(f"Connecting to: {client_uri}")
        
        async with websockets.connect(client_uri) as websocket:
            print("✅ Connected to backend WebSocket")
            
            # Test different types of client logs
            test_logs = [
                {
                    "type": "client_log",
                    "task_id": "system",
                    "level": "info",
                    "message": "Loaded existing machine ID: 60cf84ad30b5_ubuntu_60f73272",
                    "logger": "client",
                    "context": {"action": "machine_startup"},
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                },
                {
                    "type": "client_log", 
                    "task_id": "system",
                    "level": "info",
                    "message": "Starting AI Linux Client...",
                    "logger": "client", 
                    "context": {"action": "client_startup"},
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                },
                {
                    "type": "client_log",
                    "task_id": "eea9cf10-adff-4e0c-ac20-dc947b7bafdf",
                    "level": "info",
                    "message": "Executing command for task eea9cf10-adff-4e0c-ac20-dc947b7bafdf, subtask task_1, attempt 1: which nmap",
                    "logger": "client",
                    "context": {
                        "subtask_id": "task_1",
                        "command": "which nmap",
                        "attempt": 1,
                        "action": "command_start"
                    },
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                },
                {
                    "type": "client_log",
                    "task_id": "eea9cf10-adff-4e0c-ac20-dc947b7bafdf", 
                    "level": "info",
                    "message": "Command completed with exit code 0",
                    "logger": "client",
                    "context": {
                        "command": "which nmap",
                        "exit_code": 0,
                        "execution_time": 0.12,
                        "action": "command_complete"
                    },
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                },
                {
                    "type": "client_log",
                    "task_id": "eea9cf10-adff-4e0c-ac20-dc947b7bafdf",
                    "level": "debug", 
                    "message": "Heartbeat sent",
                    "logger": "client",
                    "context": {"action": "heartbeat"},
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                },
                {
                    "type": "client_log",
                    "task_id": "eea9cf10-adff-4e0c-ac20-dc947b7bafdf",
                    "level": "error",
                    "message": "Command execution failed: permission denied",
                    "logger": "client",
                    "context": {
                        "command": "sudo systemctl restart service",
                        "error": "permission_denied",
                        "action": "command_error"
                    },
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }
            ]
            
            print(f"Sending {len(test_logs)} test client log messages...")
            print()
            
            for i, log_msg in enumerate(test_logs, 1):
                print(f"📤 Sending log {i}/{len(test_logs)}: [{log_msg['level']}] {log_msg['message']}")
                await websocket.send(json.dumps(log_msg))
                await asyncio.sleep(0.5)  # Small delay between messages
            
            print()
            print("✅ All test logs sent successfully!")
            print()
            print("🔍 Check the frontend TaskLogsViewer at:")
            print("   http://localhost:3000/tasks/eea9cf10-adff-4e0c-ac20-dc947b7bafdf")
            print()
            print("📋 You should see detailed client logs including:")
            print("   • Machine startup logs")
            print("   • Command execution logs")
            print("   • Heartbeat logs")
            print("   • Error logs")
            print()
            print("⏳ Keeping connection alive for 10 seconds...")
            
            # Keep connection alive to ensure logs are processed
            await asyncio.sleep(10)
            
    except ConnectionRefusedError:
        print("❌ Connection refused - make sure the backend server is running on", server_url)
    except websockets.exceptions.InvalidStatusCode as e:
        if e.status_code == 401:
            print("❌ Authentication failed - check your API_KEY")
        elif e.status_code == 404:
            print("❌ WebSocket endpoint not found - check server URL and endpoints")
        else:
            print(f"❌ WebSocket error {e.status_code}: {e}")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        print("Make sure the backend server is running and properly configured")


if __name__ == "__main__":
    print("To run this test:")
    print("1. Start the backend server (python -m uvicorn app.main:app)")
    print("2. Set API_KEY environment variable (export API_KEY=your-api-key)")
    print("3. Run this script (python test_client_logs.py)")
    print()
    
    # Run the test
    asyncio.run(test_client_logs())