import os
import json
import re
import logging
from typing import List, Dict, Any
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


class SubTask(BaseModel):
    id: str
    description: str
    command: str
    expected_output: str
    dependencies: List[str] = []


class TaskDecomposition(BaseModel):
    original_prompt: str
    subtasks: List[SubTask]
    execution_order: List[str]


class ValidationResult(BaseModel):
    is_valid: bool
    confidence: float
    error_message: str = ""
    suggested_fix: str = ""
    should_retry: bool = True


class AlternativeCommand(BaseModel):
    command: str
    description: str
    reason: str
    confidence: float
    estimated_success_rate: float


class AlternativeStrategy(BaseModel):
    alternatives: List[AlternativeCommand]
    strategy_explanation: str
    fallback_available: bool


class LLMService:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=os.getenv("GEMINI_API_KEY"),
            temperature=0.1,
            convert_system_message_to_human=True
        )
        
        self.system_prompt = """You are an expert Linux system administrator and command-line specialist. 
Your role is to help break down complex user requests into executable Linux commands and validate their outputs.

Guidelines:
1. Always provide precise, safe Linux commands
2. Consider system dependencies and prerequisites  
3. Break complex tasks into logical, sequential steps
4. Validate command outputs for correctness and safety
5. Suggest fixes for failed commands
6. Use JSON format for structured responses"""

    async def decompose_task(self, user_prompt: str, system_info: Dict[str, Any]) -> TaskDecomposition:
        """Decompose user prompt into executable subtasks"""
        
        decomposition_prompt = f"""
        System Information:
        - OS: {system_info.get('os', 'Unknown')}
        - Architecture: {system_info.get('arch', 'Unknown')}
        - Hostname: {system_info.get('hostname', 'Unknown')}
        
        User Request: "{user_prompt}"
        
        Please break this request into Linux commands. IMPORTANT GUIDELINES:
        - For simple status checks (like "is ollama running", "current user", "list files"), use 1-2 commands maximum
        - For installation/availability checks, you may use multiple approaches for thoroughness
        - Only create multiple subtasks if the request is genuinely complex or requires dependencies
        - Combine related commands when possible (e.g., use "whoami && id" instead of separate tasks)
        - Focus on efficiency and minimal steps
        - Each subtask should have a clear purpose toward answering the user's question
        
        SPECIAL HANDLING FOR VERIFICATION TASKS:
        - For "is X installed" or "check if X available" questions, create 3 verification methods:
          Method 1: PATH/which check (command -v X or which X)
          Method 2: Package manager check (dpkg/rpm/yum/apt depending on system)
          Method 3: Direct execution test (X --version or X --help or direct binary test)
        - For service/application running status (e.g., "is ollama running", "is docker running"), use these approaches:
          Method 1: Service status check (systemctl status servicename OR systemctl is-active servicename)
          Method 2: Process check (ps aux | grep servicename | grep -v grep)
          Method 3: Port/socket check if applicable (ss -tulnp | grep port OR netstat -tulnp | grep port)
        - For file/directory existence, use 3 verification approaches:
          Method 1: Direct file test (test -f or ls)
          Method 2: find command in common locations
          Method 3: locate/whereis command
        
        CRITICAL COMMAND REQUIREMENTS:
        - Always include the actual service/application name in commands (e.g., "systemctl status ollama" not "systemctl status")
        - Use complete, executable commands (e.g., "ps aux | grep ollama | grep -v grep" not just "ps aux | grep")
        - For port checks, specify the actual port number if known (ollama uses port 11434)
        - Each command must be self-contained and executable without additional parameters
        
        Return a JSON response with this structure:
        {{
            "original_prompt": "{user_prompt}",
            "subtasks": [
                {{
                    "id": "task_1",
                    "description": "Clear description of what this step does and what success means",
                    "command": "actual linux command to execute",
                    "expected_output": "what output indicates success (be specific about exit codes and content patterns)",
                    "dependencies": ["task_id_that_must_complete_first"]
                }}
            ],
            "execution_order": ["task_1", "task_2", ...]
        }}
        
        Generate commands dynamically based on the user's request:
        
        EXAMPLES:
        - "is ollama running" → Single task: "ps aux | grep ollama | grep -v grep"
        - "current user" → Single task: "whoami"
        - "is docker installed" → Multiple tasks for thorough verification
        - "list files in /home" → Single task: "ls -la /home"
        
        Important:
        - Use only safe, non-destructive commands unless explicitly requested
        - For simple status questions, prefer single, direct commands
        - For installation verification, multiple approaches are acceptable
        - Each command should be atomic and testable
        """
        
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=decomposition_prompt)
        ]
        
        response = await self.llm.ainvoke(messages)
        
        try:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
            if json_match:
                json_data = json.loads(json_match.group())
                return TaskDecomposition(**json_data)
            else:
                raise ValueError("No valid JSON found in response")
                
        except (json.JSONDecodeError, ValueError) as e:
            # Fallback: create a simple single-command task
            return TaskDecomposition(
                original_prompt=user_prompt,
                subtasks=[
                    SubTask(
                        id="task_1",
                        description=f"Execute: {user_prompt}",
                        command=user_prompt if user_prompt.strip() else "echo 'No command specified'",
                        expected_output="Command executed successfully"
                    )
                ],
                execution_order=["task_1"]
            )

    async def validate_output(self, command: str, output: str, exit_code: int, expected_output: str) -> ValidationResult:
        """Validate command execution output"""
        
        validation_prompt = f"""
        Command Executed: {command}
        Exit Code: {exit_code}
        Actual Output: {output}
        Expected Output: {expected_output}
        
        Please validate this command execution and return a JSON response:
        {{
            "is_valid": true/false,
            "confidence": 0.0-1.0,
            "error_message": "description if invalid",
            "suggested_fix": "ONLY provide an executable command, never instructions or explanations",
            "should_retry": true/false
        }}
        
        CRITICAL RULES FOR suggested_fix:
        - MUST be a single executable command (e.g., "ollama serve")
        - NEVER provide instructions or explanations
        - NEVER include phrases like "run this command" or "try running"
        - If suggesting background process, use proper syntax: "nohup ollama serve > /dev/null 2>&1 &"
        - If no fix possible, leave suggested_fix empty ""
        
        Consider:
        - Exit code (0 = success, non-zero may be expected in some cases)
        - Output content matches expected result
        - Some commands naturally return non-zero exit codes but are still valid
        
        CRITICAL: Status check commands should be considered VALID regardless of exit code if they produce meaningful output:
        - "systemctl is-active ollama" returning "inactive" (exit code 4) is VALID - it successfully determined ollama is not running
        - "ps aux | grep ollama" with no output (exit code 1) is VALID - it successfully determined no process is running
        - "which docker" returning "not found" (exit code 1) is VALID - it successfully determined docker is not in PATH
        - "ss -tulnp | grep 11434" with no output (exit code 1) is VALID - it successfully determined port is not in use
        
        Status responses like "inactive", "not found", "no process", "stopped", "failed" are VALID answers to user questions.
        The goal is to answer the user's question, not to ensure all commands return exit code 0.
        """
        
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=validation_prompt)
        ]
        
        response = await self.llm.ainvoke(messages)
        
        try:
            json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
            if json_match:
                json_data = json.loads(json_match.group())
                return ValidationResult(**json_data)
        except (json.JSONDecodeError, ValueError):
            pass
        
        # Fallback validation with smarter exit code handling
        # Check if this is a status/check command that naturally returns non-zero for valid results
        is_status_command = any(keyword in command.lower() for keyword in [
            'systemctl is-active', 'systemctl status', 'ps aux | grep', 'grep', 'which', 'dpkg', 
            'test', 'diff', 'cmp', 'find', 'locate', 'whereis', 'ss', 'netstat'
        ])
        
        # Special handling for status check commands
        if is_status_command and exit_code != 0:
            # Check if output contains meaningful status information
            status_indicators = ['inactive', 'active', 'not found', 'no process', 'failed', 'running', 'stopped']
            has_meaningful_output = any(indicator in output.lower() for indicator in status_indicators) or bool(output.strip())
            
            if has_meaningful_output:
                return ValidationResult(
                    is_valid=True,
                    confidence=0.8,
                    error_message="",
                    suggested_fix="",
                    should_retry=False
                )
        
        # For other check commands, validate based on output rather than exit code
        is_general_check = any(keyword in command.lower() for keyword in ['check', 'verify', 'list', 'show'])
        if is_general_check and exit_code != 0 and bool(output.strip()):
            return ValidationResult(
                is_valid=True,
                confidence=0.7,
                error_message="",
                suggested_fix="",
                should_retry=False
            )
        
        return ValidationResult(
            is_valid=(exit_code == 0),
            confidence=0.8 if exit_code == 0 else 0.3,
            error_message="Command failed" if exit_code != 0 else "",
            suggested_fix="Check command syntax and permissions" if exit_code != 0 else "",
            should_retry=(exit_code != 0)
        )

    async def generate_alternative_command(self, original_command: str, error_output: str, system_info: Dict[str, Any]) -> str:
        """Generate alternative command when original fails"""
        
        alternative_prompt = f"""
        Original Command: {original_command}
        Error Output: {error_output}
        System Info: {system_info}
        
        The original command failed. Please suggest an alternative Linux command that accomplishes the same goal.
        Return only the command, no additional text.
        """
        
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=alternative_prompt)
        ]
        
        response = await self.llm.ainvoke(messages)
        return response.content.strip()

    async def generate_task_summary(self, original_prompt: str, subtasks: List[dict], system_info: Dict[str, Any]) -> str:
        """Generate AI summary by analyzing all subtask outputs to answer user's exact intent"""
        
        # Collect ALL subtask outputs for comprehensive analysis
        all_outputs = []
        for i, subtask in enumerate(subtasks, 1):
            attempts = subtask.get('attempts', [])
            if attempts:
                last_attempt = attempts[-1]
                all_outputs.append({
                    'step': i,
                    'description': subtask['description'],
                    'command': last_attempt['command'],
                    'output': last_attempt['output'].strip(),
                    'exit_code': last_attempt['exit_code']
                })
        
        # Build comprehensive analysis prompt
        outputs_text = "\n".join([
            f"Step {out['step']}: {out['description']}\nCommand: {out['command']}\nOutput: {out['output']}\nExit Code: {out['exit_code']}\n"
            for out in all_outputs
        ])
        
        summary_prompt = f"""
        USER QUESTION: "{original_prompt}"
        
        COMMAND EXECUTION RESULTS:
        {outputs_text}
        
        Your task: Analyze the command outputs and provide a clear answer to the user's question. Think logically about what the outputs mean together.
        
        Analysis Guidelines:
        - For installation/availability checks:
          * If "command -v program" returns a path, the program IS installed and available
          * If "dpkg -s program" says not installed, it means not installed via package manager
          * Both can be true - software installed manually but not via package manager
        - For verification questions:
          * Focus on whether the user's main question is answered (e.g., "is X installed?")
          * Combine outputs logically to reach a conclusion
        - For status checks:
          * Look at exit codes and output patterns together
          * Determine the actual state/status being asked about
        
        Provide a clear, definitive answer that directly addresses what the user wanted to know.
        Answer in 1-2 sentences with your conclusion.
        """
        
        messages = [
            SystemMessage(content="You are an expert system administrator who analyzes command outputs and provides clear, logical conclusions. You combine technical evidence to answer user questions definitively."),
            HumanMessage(content=summary_prompt)
        ]
        
        response = await self.llm.ainvoke(messages)
        return response.content.strip()

    async def generate_alternative_commands(self, original_command: str, failure_reason: str, 
                                          system_info: Dict[str, Any], process_metrics: Dict[str, Any] = None) -> AlternativeStrategy:
        """Generate alternative commands when original command fails or hangs"""
        
        alternative_prompt = f"""
        ORIGINAL COMMAND: {original_command}
        FAILURE REASON: {failure_reason}
        SYSTEM INFO: {system_info}
        PROCESS METRICS: {process_metrics or {}}
        
        The original command has failed or is hanging. Generate 2-3 alternative commands that achieve the same goal.
        
        Consider these alternative strategies:
        1. Different tool/utility for same purpose (e.g., apt → dpkg, wget → curl)
        2. Different flags/options (e.g., verbose mode, different output format)
        3. Fallback approaches (e.g., manual steps if automated approach fails)
        4. System-specific alternatives based on the detected environment
        
        CRITICAL REQUIREMENTS:
        - Each alternative must be a SINGLE EXECUTABLE COMMAND (no instructions)
        - Commands must be safe and appropriate for the system
        - Provide realistic success rate estimates based on common scenarios
        - Include brief explanation of why each alternative might work better
        
        Return JSON response with this structure:
        {{
            "alternatives": [
                {{
                    "command": "actual executable command",
                    "description": "What this command does",
                    "reason": "Why this might work when original failed",
                    "confidence": 0.0-1.0,
                    "estimated_success_rate": 0.0-1.0
                }}
            ],
            "strategy_explanation": "Overall strategy for these alternatives",
            "fallback_available": true/false
        }}
        
        EXAMPLES of good alternatives:
        - Original: "apt install package" → Alternative: "dpkg -i /path/to/package.deb"
        - Original: "wget https://example.com" → Alternative: "curl -O https://example.com"
        - Original: "systemctl status service" → Alternative: "ps aux | grep service"
        """
        
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=alternative_prompt)
        ]
        
        try:
            response = await self.llm.ainvoke(messages)
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
            if json_match:
                json_data = json.loads(json_match.group())
                return AlternativeStrategy(**json_data)
            else:
                raise ValueError("No valid JSON found in response")
                
        except (json.JSONDecodeError, ValueError) as e:
            # Fallback: create simple alternatives based on heuristics
            return self._generate_heuristic_alternatives(original_command, failure_reason)

    def _generate_heuristic_alternatives(self, original_command: str, failure_reason: str) -> AlternativeStrategy:
        """Generate alternatives using built-in heuristics when LLM fails"""
        alternatives = []
        command_lower = original_command.lower().strip()
        
        # Package management alternatives
        if any(pkg_cmd in command_lower for pkg_cmd in ['apt install', 'apt-get install']):
            if 'install' in command_lower:
                package_name = command_lower.split()[-1]
                alternatives.extend([
                    AlternativeCommand(
                        command=f"apt update && apt install {package_name}",
                        description="Update package lists before installation",
                        reason="Package lists might be outdated",
                        confidence=0.8,
                        estimated_success_rate=0.7
                    ),
                    AlternativeCommand(
                        command=f"apt search {package_name}",
                        description="Search for package to verify availability",
                        reason="Package name might be incorrect",
                        confidence=0.6,
                        estimated_success_rate=0.9
                    )
                ])
        
        # Network operation alternatives
        elif any(net_cmd in command_lower for net_cmd in ['wget', 'curl']):
            if 'wget' in command_lower:
                url = original_command.split()[-1]
                alternatives.append(
                    AlternativeCommand(
                        command=f"curl -O {url}",
                        description="Use curl instead of wget",
                        reason="curl might handle the URL differently",
                        confidence=0.8,
                        estimated_success_rate=0.8
                    )
                )
            elif 'curl' in command_lower:
                url = original_command.split()[-1]
                alternatives.append(
                    AlternativeCommand(
                        command=f"wget {url}",
                        description="Use wget instead of curl",
                        reason="wget might handle the URL differently",
                        confidence=0.8,
                        estimated_success_rate=0.8
                    )
                )
        
        # Service management alternatives
        elif 'systemctl' in command_lower:
            service_name = command_lower.split()[-1]
            if 'status' in command_lower:
                alternatives.extend([
                    AlternativeCommand(
                        command=f"ps aux | grep {service_name}",
                        description="Check if service process is running",
                        reason="Direct process check bypasses systemctl",
                        confidence=0.7,
                        estimated_success_rate=0.9
                    ),
                    AlternativeCommand(
                        command=f"service {service_name} status",
                        description="Use legacy service command",
                        reason="Some systems prefer service over systemctl",
                        confidence=0.6,
                        estimated_success_rate=0.7
                    )
                ])
        
        # File operation alternatives
        elif any(file_cmd in command_lower for file_cmd in ['ls', 'find']):
            if 'ls' in command_lower and 'hanging' in failure_reason.lower():
                path = original_command.split()[-1] if len(original_command.split()) > 1 else '.'
                alternatives.append(
                    AlternativeCommand(
                        command=f"find {path} -maxdepth 1 -type f",
                        description="Use find to list files",
                        reason="find might handle large directories better",
                        confidence=0.7,
                        estimated_success_rate=0.8
                    )
                )
        
        # Default fallbacks
        if not alternatives:
            alternatives.append(
                AlternativeCommand(
                    command="echo 'No specific alternative available'",
                    description="Placeholder command",
                    reason="No heuristic alternatives found",
                    confidence=0.1,
                    estimated_success_rate=0.1
                )
            )
        
        return AlternativeStrategy(
            alternatives=alternatives,
            strategy_explanation="Generated using heuristic fallback rules",
            fallback_available=len(alternatives) > 0
        )

    async def analyze_hanging_command(self, command: str, output_so_far: str, 
                                    process_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze why a command might be hanging and suggest interventions"""
        
        analysis_prompt = f"""
        HANGING COMMAND ANALYSIS
        
        Command: {command}
        Output so far: {output_so_far[-1000:] if output_so_far else "No output"}
        Process Metrics: {process_metrics}
        
        Analyze why this command might be hanging and provide recommendations.
        
        Consider these common hanging scenarios:
        1. Waiting for user input (password, confirmation)
        2. Network timeout (slow connection, unreachable host)
        3. Resource exhaustion (out of memory, disk space)
        4. Infinite loop or stuck process
        5. Waiting for external resource (file lock, service)
        6. Large data processing without progress indication
        
        Return JSON response:
        {{
            "likely_cause": "most probable reason for hanging",
            "confidence": 0.0-1.0,
            "recommended_action": "kill|wait|provide_input|alternative",
            "intervention_command": "command to resolve if applicable",
            "wait_time_suggestion": "seconds to wait before taking action",
            "explanation": "detailed explanation of the analysis"
        }}
        """
        
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=analysis_prompt)
        ]
        
        try:
            response = await self.llm.ainvoke(messages)
            json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            logger.error(f"Failed to analyze hanging command: {e}")
        
        # Fallback analysis
        return {
            "likely_cause": "unknown",
            "confidence": 0.5,
            "recommended_action": "alternative",
            "intervention_command": "",
            "wait_time_suggestion": "30",
            "explanation": "Unable to perform detailed analysis, suggesting alternative approach"
        }


# Global LLM service instance
llm_service = LLMService()