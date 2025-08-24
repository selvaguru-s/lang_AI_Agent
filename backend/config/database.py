import os
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional


class Database:
    client: Optional[AsyncIOMotorClient] = None
    database = None


database = Database()


async def get_database():
    return database.database


async def connect_to_mongo():
    """Create database connection"""
    database.client = AsyncIOMotorClient(
        os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    )
    database.database = database.client.ai_linux_agent
    
    # Create indexes for better performance
    await database.database.users.create_index("firebase_uid", unique=True)
    await database.database.users.create_index("api_key", unique=True)
    await database.database.client_machines.create_index("machine_id", unique=True)
    await database.database.task_executions.create_index("user_id")
    await database.database.task_executions.create_index("machine_id")
    
    print("Connected to MongoDB")


async def close_mongo_connection():
    """Close database connection"""
    if database.client:
        database.client.close()
        print("Disconnected from MongoDB")