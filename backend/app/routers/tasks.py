from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import List, Dict, Any
from utils.auth import get_current_user
from utils.llm_service import llm_service
from models.user import User, TaskExecution
from config.database import get_database
import uuid
from datetime import datetime


router = APIRouter()


class TaskRequest(BaseModel):
    prompt: str
    machine_id: str


class TaskResponse(BaseModel):
    task_id: str
    status: str
    subtasks: List[dict]


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    current_subtask_index: int
    total_subtasks: int
    error_message: str = None


@router.post("/", response_model=TaskResponse)
async def create_task(
    request: TaskRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new task by decomposing user prompt into subtasks
    """
    try:
        db = await get_database()
        
        # Verify machine belongs to user
        machine = await db.client_machines.find_one({
            "machine_id": request.machine_id,
            "is_active": True
        })
        
        if not machine:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client machine not found or inactive"
            )
        
        # Check if machine is associated with user
        if request.machine_id not in current_user.client_machines:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Client machine not associated with user"
            )
        
        # Get system info for the machine
        system_info = {
            "os": machine.get("os_info", "Linux"),
            "arch": machine.get("architecture", "x86_64"),
            "hostname": machine.get("hostname", "unknown")
        }
        
        # Decompose task using LLM
        task_decomposition = await llm_service.decompose_task(
            request.prompt, 
            system_info
        )
        
        # Create task execution record
        task_id = str(uuid.uuid4())
        task_execution = TaskExecution(
            task_id=task_id,
            user_id=str(current_user.id),
            machine_id=request.machine_id,
            original_prompt=request.prompt,
            subtasks=[subtask.dict() for subtask in task_decomposition.subtasks],
            status="pending"
        )
        
        # Save to database
        await db.task_executions.insert_one(task_execution.dict())
        
        # Start task execution by sending to client
        from app.routers.websocket import start_task_execution
        execution_started = await start_task_execution(
            task_id, 
            current_user.firebase_uid, 
            request.machine_id
        )
        
        response_status = "running" if execution_started else "pending"
        
        return TaskResponse(
            task_id=task_id,
            status=response_status,
            subtasks=[subtask.dict() for subtask in task_decomposition.subtasks]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create task: {str(e)}"
        )


@router.get("/list")
async def list_user_tasks(
    current_user: User = Depends(get_current_user),
    limit: int = 20,
    offset: int = 0
):
    """
    List all tasks for the current user
    """
    try:
        db = await get_database()
        
        cursor = db.task_executions.find(
            {"user_id": str(current_user.id)}
        ).sort("created_at", -1).skip(offset).limit(limit)
        
        tasks = []
        async for task in cursor:
            tasks.append({
                "task_id": task["task_id"],
                "original_prompt": task["original_prompt"],
                "status": task["status"],
                "machine_id": task["machine_id"],
                "created_at": task["created_at"],
                "completed_at": task.get("completed_at"),
                "current_subtask_index": task.get("current_subtask_index", 0),
                "subtasks": task.get("subtasks", [])
            })
        
        return tasks
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list tasks: {str(e)}"
        )


@router.get("/status/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(
    task_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get current status of a task
    """
    try:
        db = await get_database()
        
        task = await db.task_executions.find_one({
            "task_id": task_id,
            "user_id": str(current_user.id)
        })
        
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        return TaskStatusResponse(
            task_id=task_id,
            status=task["status"],
            current_subtask_index=task["current_subtask_index"],
            total_subtasks=len(task["subtasks"]),
            error_message=task.get("error_message")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get task status: {str(e)}"
        )


@router.delete("/{task_id}")
async def cancel_task(
    task_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Cancel a running task
    """
    try:
        db = await get_database()
        
        result = await db.task_executions.update_one(
            {
                "task_id": task_id,
                "user_id": str(current_user.id),
                "status": {"$in": ["pending", "running"]}
            },
            {
                "$set": {
                    "status": "cancelled",
                    "completed_at": datetime.utcnow()
                }
            }
        )
        
        if result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found or cannot be cancelled"
            )
        
        return {"message": "Task cancelled successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel task: {str(e)}"
        )


@router.get("/{task_id}")
async def get_task_details(
    task_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed information about a task including subtasks and execution history
    """
    try:
        db = await get_database()
        
        task = await db.task_executions.find_one({
            "task_id": task_id,
            "user_id": str(current_user.id)
        })
        
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        # Convert ObjectId to string for JSON serialization
        if '_id' in task:
            task['_id'] = str(task['_id'])
        
        return task
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get task details: {str(e)}"
        )


@router.post("/{task_id}/generate-summary")
async def generate_ai_summary(
    task_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Generate AI summary for a completed task and send via WebSocket
    """
    try:
        db = await get_database()
        
        task = await db.task_executions.find_one({
            "task_id": task_id,
            "user_id": str(current_user.id)
        })
        
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        # Only generate summary for completed tasks
        if task["status"] not in ["completed", "failed"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Task must be completed to generate summary"
            )
        
        # Get system info for the task
        machine = await db.client_machines.find_one({
            "machine_id": task["machine_id"]
        })
        
        system_info = {
            "os": machine.get("os_info", "Linux") if machine else "Linux",
            "arch": machine.get("architecture", "x86_64") if machine else "x86_64",
            "hostname": machine.get("hostname", "unknown") if machine else "unknown"
        }
        
        # Generate AI summary
        ai_summary = await llm_service.generate_task_summary(
            task["original_prompt"],
            task["subtasks"],
            system_info
        )
        
        # Update task with AI summary
        await db.task_executions.update_one(
            {"task_id": task_id},
            {"$set": {
                "ai_summary": ai_summary,
                "ai_summary_generated_at": datetime.utcnow()
            }}
        )
        
        # Send AI summary update via WebSocket
        from app.routers.websocket import send_ai_summary_to_user
        await send_ai_summary_to_user(
            current_user.firebase_uid, 
            task_id, 
            ai_summary, 
            task["machine_id"]
        )
        
        return {
            "message": "AI summary generated successfully",
            "ai_summary": ai_summary
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate AI summary: {str(e)}"
        )