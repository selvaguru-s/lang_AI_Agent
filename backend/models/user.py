from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from bson import ObjectId


class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type, _handler):
        from pydantic_core import core_schema
        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(),
            python_schema=core_schema.union_schema([
                core_schema.is_instance_schema(ObjectId),
                core_schema.chain_schema([
                    core_schema.str_schema(),
                    core_schema.no_info_plain_validator_function(cls.validate),
                ])
            ]),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda x: str(x)
            ),
        )

    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return v
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)


class ClientMachine(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    machine_id: str = Field(..., description="Unique client machine identifier")
    hostname: str
    os_info: str
    architecture: str
    mac_address: str
    last_seen: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True


class User(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    firebase_uid: str = Field(..., unique=True)
    email: str
    name: str
    api_key: str = Field(..., unique=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True
    client_machines: List[str] = Field(default_factory=list)  # List of machine_ids
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True


class TaskExecution(BaseModel):
    task_id: str
    user_id: str
    machine_id: str
    original_prompt: str
    subtasks: List[dict]
    current_subtask_index: int = 0
    status: str = "pending"  # pending, running, completed, failed
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True


class SubtaskAttempt(BaseModel):
    attempt_number: int
    command: str
    output: str
    exit_code: int
    validation_result: dict
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        arbitrary_types_allowed = True