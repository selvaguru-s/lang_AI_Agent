from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import logging

from utils.auth import get_current_user_api_key
from utils.llm_service import llm_service
from models.user import User

router = APIRouter()
logger = logging.getLogger(__name__)


class AlternativeCommandRequest(BaseModel):
    original_command: str
    failure_reason: str
    system_info: Dict[str, Any]
    process_metrics: Optional[Dict[str, Any]] = None


class AlternativeCommandResponse(BaseModel):
    command: str
    description: str
    reason: str
    confidence: float
    estimated_success_rate: float


class AlternativeStrategyResponse(BaseModel):
    alternatives: List[AlternativeCommandResponse]
    strategy_explanation: str
    fallback_available: bool


class HangingAnalysisRequest(BaseModel):
    command: str
    output_so_far: str = ""
    process_metrics: Dict[str, Any] = {}
    prompt: Optional[str] = None  # For LLM analysis prompt


class HangingAnalysisResponse(BaseModel):
    likely_cause: str
    confidence: float
    recommended_action: str
    intervention_command: str
    wait_time_suggestion: str
    explanation: str


class LLMAnalysisRequest(BaseModel):
    prompt: str
    command: Optional[str] = None
    output: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class LLMAnalysisResponse(BaseModel):
    status: str
    confidence: float
    reasoning: str
    should_kill: bool
    suggested_alternative: Optional[str] = None
    needs_user_input: bool = False
    estimated_remaining_time: int = 30


@router.post("/generate-alternatives", response_model=AlternativeStrategyResponse)
async def generate_alternative_commands(
    request: AlternativeCommandRequest,
    user: User = Depends(get_current_user_api_key)
):
    """Generate alternative commands for failed or hanging commands"""
    try:
        logger.info(f"Generating alternatives for command: {request.original_command}")
        
        # Use LLM service to generate alternatives
        alternative_strategy = await llm_service.generate_alternative_commands(
            original_command=request.original_command,
            failure_reason=request.failure_reason,
            system_info=request.system_info,
            process_metrics=request.process_metrics
        )
        
        # Convert to response format
        alternatives = []
        for alt in alternative_strategy.alternatives:
            alternatives.append(AlternativeCommandResponse(
                command=alt.command,
                description=alt.description,
                reason=alt.reason,
                confidence=alt.confidence,
                estimated_success_rate=alt.estimated_success_rate
            ))
        
        response = AlternativeStrategyResponse(
            alternatives=alternatives,
            strategy_explanation=alternative_strategy.strategy_explanation,
            fallback_available=alternative_strategy.fallback_available
        )
        
        logger.info(f"Generated {len(alternatives)} alternatives for user {user.email}")
        return response
        
    except Exception as e:
        logger.error(f"Error generating alternative commands: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate alternative commands")


@router.post("/analyze-hanging", response_model=LLMAnalysisResponse)
async def analyze_hanging_command(
    request: HangingAnalysisRequest,
    user: User = Depends(get_current_user_api_key)
):
    """Analyze command output using LLM to determine if it should be killed"""
    try:
        logger.info(f"Performing LLM analysis for command: {request.command}")
        
        # If custom prompt provided, use it directly for LLM analysis
        if request.prompt:
            # Use LLM service directly with the provided prompt
            from langchain.schema import HumanMessage, SystemMessage
            
            messages = [
                SystemMessage(content="You are an expert Linux system administrator analyzing command execution. Always respond with valid JSON only."),
                HumanMessage(content=request.prompt)
            ]
            
            response_content = await llm_service.llm.ainvoke(messages)
            
            # Parse JSON response
            import json
            import re
            
            try:
                json_match = re.search(r'\{.*\}', response_content.content, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                    return LLMAnalysisResponse(
                        status=result.get('status', 'running'),
                        confidence=result.get('confidence', 0.5),
                        reasoning=result.get('reasoning', 'LLM analysis completed'),
                        should_kill=result.get('should_kill', False),
                        suggested_alternative=result.get('suggested_alternative'),
                        needs_user_input=result.get('needs_user_input', False),
                        estimated_remaining_time=result.get('estimated_remaining_time', 30)
                    )
            except (json.JSONDecodeError, KeyError):
                pass
            
            # Fallback response if JSON parsing fails
            return LLMAnalysisResponse(
                status="running",
                confidence=0.5,
                reasoning="Unable to parse LLM response",
                should_kill=False,
                estimated_remaining_time=30
            )
        
        # Default hanging analysis
        analysis = await llm_service.analyze_hanging_command(
            command=request.command,
            output_so_far=request.output_so_far,
            process_metrics=request.process_metrics
        )
        
        return LLMAnalysisResponse(
            status="hanging" if analysis.get("recommended_action") == "kill" else "running",
            confidence=analysis.get("confidence", 0.5),
            reasoning=analysis.get("explanation", "Analysis not available"),
            should_kill=analysis.get("recommended_action") == "kill",
            suggested_alternative=analysis.get("intervention_command", ""),
            needs_user_input=False,
            estimated_remaining_time=int(analysis.get("wait_time_suggestion", "30"))
        )
        
    except Exception as e:
        logger.error(f"Error analyzing hanging command: {e}")
        # Return safe fallback instead of raising exception
        return LLMAnalysisResponse(
            status="running",
            confidence=0.3,
            reasoning=f"Analysis failed: {str(e)}",
            should_kill=False,
            estimated_remaining_time=30
        )


@router.get("/command-patterns")
async def get_command_patterns(user: User = Depends(get_current_user_api_key)):
    """Get common command patterns and their typical behaviors"""
    patterns = {
        "package_management": {
            "commands": ["apt install", "yum install", "pip install", "npm install"],
            "typical_duration": "30-300 seconds",
            "hanging_indicators": ["no progress bar updates", "network timeouts"],
            "common_alternatives": ["update package lists first", "use different package manager"]
        },
        "network_operations": {
            "commands": ["wget", "curl", "ssh", "scp"],
            "typical_duration": "5-120 seconds",
            "hanging_indicators": ["connection timeouts", "DNS resolution failures"],
            "common_alternatives": ["different URL", "timeout settings", "alternative tools"]
        },
        "system_services": {
            "commands": ["systemctl", "service"],
            "typical_duration": "1-30 seconds",
            "hanging_indicators": ["service startup failures", "dependency issues"],
            "common_alternatives": ["check service dependencies", "manual service management"]
        },
        "file_operations": {
            "commands": ["ls", "find", "cp", "mv"],
            "typical_duration": "1-60 seconds",
            "hanging_indicators": ["large directory traversal", "permission issues"],
            "common_alternatives": ["limit depth", "different tools", "permission fixes"]
        }
    }
    
    return patterns


@router.get("/health-metrics")
async def get_health_metrics(user: User = Depends(get_current_user_api_key)):
    """Get information about process health monitoring"""
    metrics_info = {
        "health_indicators": {
            "cpu_usage": "Process CPU utilization percentage",
            "memory_usage": "Process memory consumption in MB",
            "output_activity": "Time since last output",
            "interactive_status": "Whether process is waiting for input"
        },
        "timeout_thresholds": {
            "quick_info": {"no_output": 10, "max_total": 30},
            "package_management": {"no_output": 60, "max_total": 600},
            "network_operation": {"no_output": 45, "max_total": 300},
            "compilation": {"no_output": 120, "max_total": 1800}
        },
        "hanging_detection": {
            "criteria": [
                "No output for specified duration",
                "CPU usage below threshold",
                "No memory growth",
                "Process not responding to signals"
            ],
            "intervention_strategies": [
                "Generate alternative command",
                "Graceful termination",
                "Force termination",
                "User notification"
            ]
        }
    }
    
    return metrics_info