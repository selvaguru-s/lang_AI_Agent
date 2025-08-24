#!/usr/bin/env python3
"""
Test script to simulate first-time client registration
"""
import asyncio
import sys
import os

# Add backend path
sys.path.insert(0, 'backend')
os.chdir('backend')

from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

async def test_first_time_registration():
    """Test the flow for a first-time user with a new API key"""
    client = AsyncIOMotorClient(os.getenv('MONGODB_URL', 'mongodb://localhost:27017'))
    db = client.ai_linux_agent
    
    api_key = 'Lo0EibSm3bCKUYjdTunliGbxa3a7mTfl'
    machine_id = '60cf84ad30b5_ubuntu_60f73272'
    
    print("=== First-time Registration Test ===")
    
    # 1. Check user exists
    user = await db.users.find_one({'api_key': api_key})
    if not user:
        print("❌ User not found with that API key")
        return
    
    print(f"✅ User found: {user['email']}")
    
    # 2. Clear client_machines to simulate first-time
    await db.users.update_one(
        {'_id': user['_id']},
        {'$set': {'client_machines': []}}
    )
    print("🔄 Cleared client_machines to simulate first-time registration")
    
    # 3. Check current state
    updated_user = await db.users.find_one({'_id': user['_id']})
    print(f"📋 Current client_machines: {updated_user.get('client_machines', [])}")
    
    # 4. Check if machine exists
    machine = await db.client_machines.find_one({'machine_id': machine_id})
    if machine:
        print(f"✅ Machine exists: {machine['hostname']}")
    else:
        print("❌ Machine not found")
    
    print("\n=== Now run the client to test first-time registration ===")
    print("cd /home/Linux_agent/v4_agent/ai-linux-agent/client")
    print("source venv/bin/activate")
    print("python3 run_client.py")

if __name__ == "__main__":
    asyncio.run(test_first_time_registration())