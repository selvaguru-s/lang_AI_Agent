#!/usr/bin/env python3
import asyncio
import sys
import os

# Add backend path
sys.path.insert(0, 'backend')

from config.database import get_database

async def debug_database():
    db = await get_database()
    
    # Find user
    user = await db.users.find_one({'api_key': '9mGJ3k2WVV9IQT4fqBbpZrK43g6VabsW'})
    print("User found:")
    print(f"  ID: {user['_id']}")
    print(f"  Email: {user['email']}")
    print(f"  Client machines: {user.get('client_machines', [])}")
    
    # Find all client machines
    print("\nAll client machines:")
    async for machine in db.client_machines.find():
        print(f"  Machine ID: {machine['machine_id']}")
        print(f"  Hostname: {machine['hostname']}")
        print(f"  Active: {machine.get('is_active', False)}")
        print()

if __name__ == "__main__":
    asyncio.run(debug_database())