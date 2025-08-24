#!/usr/bin/env python3
"""
AI Linux Agent Client Runner

This script runs the AI Linux Agent client that connects to the backend server
and executes commands remotely.

Usage:
    python run_client.py [--api-key API_KEY] [--server-url SERVER_URL]
    
Environment variables:
    API_KEY: API key obtained from the web dashboard
    SERVER_URL: WebSocket URL of the backend server (default: ws://localhost:8000)
    LOG_LEVEL: Logging level (DEBUG, INFO, WARNING, ERROR)
"""

import argparse
import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add src directory to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from client import AILinuxClient


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="AI Linux Agent Client",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        "--api-key",
        help="API key for authentication (can also use API_KEY env var)"
    )
    
    parser.add_argument(
        "--server-url",
        default=os.getenv("SERVER_URL", "ws://localhost:8000"),
        help="WebSocket URL of the backend server (default: ws://localhost:8000)"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Set logging level (default: INFO)"
    )
    
    parser.add_argument(
        "--heartbeat-interval",
        type=int,
        default=30,
        help="Heartbeat interval in seconds (default: 30)"
    )
    
    return parser.parse_args()


def setup_environment(args):
    """Set up environment variables from command line arguments"""
    if args.api_key:
        os.environ["API_KEY"] = args.api_key
    
    if args.server_url:
        os.environ["SERVER_URL"] = args.server_url
        
    if args.log_level:
        os.environ["LOG_LEVEL"] = args.log_level
        
    if args.heartbeat_interval:
        os.environ["HEARTBEAT_INTERVAL"] = str(args.heartbeat_interval)


def validate_environment():
    """Validate required environment variables"""
    api_key = os.getenv("API_KEY")
    
    if not api_key:
        print("Error: API_KEY is required either as environment variable or --api-key argument")
        print("Get your API key from the web dashboard after logging in with Firebase")
        return False
    
    return True


async def main():
    """Main entry point"""
    args = parse_arguments()
    setup_environment(args)
    
    if not validate_environment():
        sys.exit(1)
    
    print("AI Linux Agent Client")
    print("=" * 30)
    print(f"Server URL: {os.getenv('SERVER_URL')}")
    print(f"Log Level: {os.getenv('LOG_LEVEL')}")
    print(f"Heartbeat Interval: {os.getenv('HEARTBEAT_INTERVAL')}s")
    print()
    
    try:
        client = AILinuxClient()
        await client.run()
    except KeyboardInterrupt:
        print("\nClient interrupted by user")
    except Exception as e:
        print(f"Client failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutdown complete")
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)