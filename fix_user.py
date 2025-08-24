#!/usr/bin/env python3
import asyncio
import sys
import os

# Add backend path  
sys.path.insert(0, 'backend')
os.chdir('backend')

from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

async def fix_user():
    client = AsyncIOMotorClient(os.getenv("MONGODB_URL", "mongodb://localhost:27017"))
    db = client.ai_linux_agent
    
    # Find user
    user = await db.users.find_one({'api_key': '9mGJ3k2WVV9IQT4fqBbpZrK43g6VabsW'})
    print(f"User found: {user['email']}")
    print(f"Current client_machines: {user.get('client_machines', [])}")
    
    # Find all machines
    machines = []
    async for machine in db.client_machines.find():
        machines.append(machine['machine_id'])
        print(f"Found machine: {machine['machine_id']} - {machine['hostname']}")
    
    # Update user with all machine IDs
    result = await db.users.update_one(
        {'_id': user['_id']},
        {'$set': {'client_machines': machines}}
    )
    
    print(f"Updated user: {result.modified_count} records modified")
    
    # Verify update
    updated_user = await db.users.find_one({'_id': user['_id']})
    print(f"New client_machines: {updated_user.get('client_machines', [])}")

if __name__ == "__main__":
    asyncio.run(fix_user())