from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import List, Dict, Any
from utils.auth import get_current_user
from models.user import User, ClientMachine
from config.database import get_database
from datetime import datetime
import hashlib
import uuid


router = APIRouter()


class ClientRegistrationRequest(BaseModel):
    hostname: str
    os_info: str
    architecture: str
    mac_address: str


class ClientRegistrationResponse(BaseModel):
    machine_id: str
    status: str
    message: str


class ClientInfo(BaseModel):
    machine_id: str
    hostname: str
    os_info: str
    architecture: str
    last_seen: datetime
    is_active: bool


def generate_machine_id(hostname: str, mac_address: str) -> str:
    """Generate unique machine ID using format: mac_hostname_uniquenumber"""
    # Clean MAC address (remove colons)
    clean_mac = mac_address.replace(":", "")
    
    # Generate unique 8-character number based on system info
    system_info = f"{hostname}_{mac_address}_salt_2024"
    hash_obj = hashlib.sha256(system_info.encode())
    unique_num = hash_obj.hexdigest()[:8]
    
    # Format: macaddress_hostname_uniquenumber
    machine_id = f"{clean_mac}_{hostname}_{unique_num}"
    return machine_id


@router.post("/register", response_model=ClientRegistrationResponse)
async def register_client(
    request: ClientRegistrationRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Register a new client machine with the user
    """
    try:
        db = await get_database()
        
        # Generate unique machine ID
        machine_id = generate_machine_id(request.hostname, request.mac_address)
        print(f"Registration: Generated machine_id: {machine_id} for user: {current_user.email}")
        
        # Check if machine already exists
        existing_machine = await db.client_machines.find_one({
            "machine_id": machine_id
        })
        
        if existing_machine:
            print(f"Registration: Updating existing machine {machine_id}")
            # Update existing machine info
            await db.client_machines.update_one(
                {"machine_id": machine_id},
                {
                    "$set": {
                        "hostname": request.hostname,
                        "os_info": request.os_info,
                        "architecture": request.architecture,
                        "last_seen": datetime.utcnow(),
                        "is_active": True
                    }
                }
            )
            
            # Ensure machine is in user's client list - use API key lookup like previous examples
            user_check = await db.users.find_one({"api_key": current_user.api_key})
            if user_check:
                current_machines = user_check.get("client_machines", [])
                
                if machine_id not in current_machines:
                    result = await db.users.update_one(
                        {"api_key": current_user.api_key},
                        {"$push": {"client_machines": machine_id}}
                    )
                    print(f"Added machine {machine_id} to existing user {current_user.email}: {result.modified_count} records modified")
                else:
                    print(f"Machine {machine_id} already exists for existing user {current_user.email}")
            else:
                print(f"Error: Could not find user {current_user.email} in database")
            
            return ClientRegistrationResponse(
                machine_id=machine_id,
                status="updated",
                message="Client machine updated successfully"
            )
        
        print(f"Registration: Creating new machine {machine_id}")
        # Create new machine record
        new_machine = ClientMachine(
            machine_id=machine_id,
            hostname=request.hostname,
            os_info=request.os_info,
            architecture=request.architecture,
            mac_address=request.mac_address
        )
        
        await db.client_machines.insert_one(new_machine.dict(by_alias=True))
        
        # Add machine to user's client list - ensure it's always added
        # First check if it's already there - use API key lookup like previous examples
        user_check = await db.users.find_one({"api_key": current_user.api_key})
        if user_check:
            current_machines = user_check.get("client_machines", [])
            
            if machine_id not in current_machines:
                result = await db.users.update_one(
                    {"api_key": current_user.api_key},
                    {"$push": {"client_machines": machine_id}}
                )
                print(f"Added machine {machine_id} to user {current_user.email}: {result.modified_count} records modified")
            else:
                print(f"Machine {machine_id} already exists for user {current_user.email}")
        else:
            print(f"Error: Could not find user {current_user.email} in database for new machine")
        
        return ClientRegistrationResponse(
            machine_id=machine_id,
            status="registered",
            message="Client machine registered successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to register client: {str(e)}"
        )


@router.get("/list", response_model=List[ClientInfo])
async def list_client_machines(
    current_user: User = Depends(get_current_user)
):
    """
    List all client machines for the current user
    """
    try:
        db = await get_database()
        
        # Get all machines for the user
        cursor = db.client_machines.find({
            "machine_id": {"$in": current_user.client_machines}
        }).sort("last_seen", -1)
        
        machines = []
        async for machine in cursor:
            machines.append(ClientInfo(
                machine_id=machine["machine_id"],
                hostname=machine["hostname"],
                os_info=machine["os_info"],
                architecture=machine["architecture"],
                last_seen=machine["last_seen"],
                is_active=machine["is_active"]
            ))
        
        return machines
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list client machines: {str(e)}"
        )


@router.get("/{machine_id}")
async def get_client_details(
    machine_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed information about a specific client machine
    """
    try:
        # Verify machine belongs to user
        if machine_id not in current_user.client_machines:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Client machine not found or access denied"
            )
        
        db = await get_database()
        machine = await db.client_machines.find_one({"machine_id": machine_id})
        
        if not machine:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client machine not found"
            )
        
        # Get recent tasks for this machine
        recent_tasks = []
        cursor = db.task_executions.find({
            "machine_id": machine_id,
            "user_id": str(current_user.id)
        }).sort("created_at", -1).limit(10)
        
        async for task in cursor:
            recent_tasks.append({
                "task_id": task["task_id"],
                "original_prompt": task["original_prompt"],
                "status": task["status"],
                "created_at": task["created_at"],
                "completed_at": task.get("completed_at")
            })
        
        return {
            "machine_info": machine,
            "recent_tasks": recent_tasks
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get client details: {str(e)}"
        )


@router.delete("/{machine_id}")
async def remove_client_machine(
    machine_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Remove a client machine from user's account
    """
    try:
        # Verify machine belongs to user
        if machine_id not in current_user.client_machines:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Client machine not found or access denied"
            )
        
        db = await get_database()
        
        # Mark machine as inactive
        await db.client_machines.update_one(
            {"machine_id": machine_id},
            {"$set": {"is_active": False}}
        )
        
        # Remove from user's client list
        await db.users.update_one(
            {"_id": current_user.id},
            {"$pull": {"client_machines": machine_id}}
        )
        
        return {"message": "Client machine removed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove client machine: {str(e)}"
        )


@router.post("/{machine_id}/ping")
async def ping_client_machine(
    machine_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Ping a client machine to check if it's online
    """
    try:
        # Verify machine belongs to user
        if machine_id not in current_user.client_machines:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Client machine not found or access denied"
            )
        
        # Import here to avoid circular imports
        from app.routers.websocket import manager
        
        # Try to send ping message to client
        ping_message = {
            "type": "ping",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        success = await manager.send_to_client(machine_id, ping_message)
        
        return {
            "machine_id": machine_id,
            "online": success,
            "message": "Ping sent successfully" if success else "Client not connected"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ping client machine: {str(e)}"
        )