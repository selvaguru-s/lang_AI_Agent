#!/usr/bin/env python3
"""
Test script to verify API key authentication
"""
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_KEY = os.getenv("API_KEY")
SERVER_URL = os.getenv("SERVER_URL", "http://192.168.1.12:8000").replace("ws://", "http://").replace("wss://", "https://")

print(f"Testing API key: {API_KEY}")
print(f"Server URL: {SERVER_URL}")

# Test 1: List clients
print("\n=== Test 1: List Clients ===")
try:
    response = requests.get(
        f"{SERVER_URL}/api/clients/list",
        headers={"Authorization": f"Bearer {API_KEY}"}
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")

# Test 2: Health check
print("\n=== Test 2: Health Check ===")
try:
    response = requests.get(f"{SERVER_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")

# Test 3: Try to access a protected endpoint
print("\n=== Test 3: Protected Endpoint Test ===")
try:
    response = requests.get(
        f"{SERVER_URL}/api/clients/60cf84ad30b5_ubuntu_60f73272",
        headers={"Authorization": f"Bearer {API_KEY}"}
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")