import re
import hashlib
import hmac
import time
from typing import Dict, List, Optional
from fastapi import HTTPException, Request, status
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded


# Rate limiting
limiter = Limiter(key_func=get_remote_address)

# Security patterns for command validation
DANGEROUS_PATTERNS = [
    # System destruction
    r'rm\s+-rf\s+/',
    r'dd\s+if=.*of=/dev/',
    r'mkfs\.',
    r'fdisk',
    r'parted',
    
    # System control
    r'shutdown',
    r'reboot',
    r'halt',
    r'poweroff',
    r'init\s+[06]',
    r'systemctl\s+(poweroff|reboot|halt)',
    
    # User management
    r'userdel',
    r'sudo\s+passwd',
    r'passwd\s+root',
    
    # Critical file modifications
    r'>\s*/etc/(passwd|shadow|sudoers)',
    r'>>\s*/etc/(passwd|shadow|sudoers)',
    r'chmod\s+777\s+/',
    r'chown\s+root\s+/',
    
    # Network/security bypass
    r'iptables\s+-F',
    r'ufw\s+disable',
    r'setenforce\s+0',
    
    # Package management risks
    r'apt\s+remove\s+.*linux-image',
    r'yum\s+remove\s+.*kernel',
    r'dnf\s+remove\s+.*kernel',
]

COMPILED_PATTERNS = [re.compile(pattern, re.IGNORECASE) for pattern in DANGEROUS_PATTERNS]


class SecurityValidator:
    def __init__(self):
        self.max_command_length = 2000
        self.max_output_length = 100000
        
    def validate_command(self, command: str) -> tuple[bool, str]:
        """
        Validate command for security risks
        Returns (is_safe, reason)
        """
        if not command or not command.strip():
            return False, "Empty command"
        
        # Length check
        if len(command) > self.max_command_length:
            return False, f"Command too long (max {self.max_command_length} chars)"
        
        # Check against dangerous patterns
        for pattern in COMPILED_PATTERNS:
            if pattern.search(command):
                return False, f"Command contains dangerous pattern: {pattern.pattern}"
        
        # Check for suspicious redirections
        if self._has_dangerous_redirections(command):
            return False, "Command contains dangerous file redirections"
        
        # Check for command chaining with dangerous commands
        if self._has_dangerous_chaining(command):
            return False, "Command contains dangerous command chaining"
        
        return True, "Command validated"
    
    def _has_dangerous_redirections(self, command: str) -> bool:
        """Check for dangerous file redirections"""
        dangerous_redirects = [
            r'>\s*/boot/',
            r'>\s*/sys/',
            r'>\s*/proc/',
            r'>\s*/dev/(?!null|zero)',
            r'>>\s*/boot/',
            r'>>\s*/sys/',
            r'>>\s*/proc/',
        ]
        
        for pattern in dangerous_redirects:
            if re.search(pattern, command, re.IGNORECASE):
                return True
        return False
    
    def _has_dangerous_chaining(self, command: str) -> bool:
        """Check for dangerous command chaining"""
        # Split by common command separators
        parts = re.split(r'[;&|]+', command)
        
        for part in parts:
            part = part.strip()
            if not part:
                continue
                
            # Check each part against patterns
            for pattern in COMPILED_PATTERNS:
                if pattern.search(part):
                    return True
        
        return False
    
    def sanitize_output(self, output: str) -> str:
        """Sanitize command output"""
        if not output:
            return ""
        
        # Truncate if too long
        if len(output) > self.max_output_length:
            output = output[:self.max_output_length] + "\n... [Output truncated]"
        
        # Remove potential ANSI escape sequences
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        output = ansi_escape.sub('', output)
        
        return output


class IPWhitelist:
    def __init__(self, whitelist: Optional[List[str]] = None):
        self.whitelist = set(whitelist) if whitelist else set()
        
    def is_allowed(self, ip: str) -> bool:
        """Check if IP is in whitelist"""
        if not self.whitelist:
            return True  # No whitelist means all IPs allowed
        return ip in self.whitelist
    
    def add_ip(self, ip: str):
        """Add IP to whitelist"""
        self.whitelist.add(ip)
    
    def remove_ip(self, ip: str):
        """Remove IP from whitelist"""
        self.whitelist.discard(ip)


class RequestValidator:
    def __init__(self):
        self.max_request_size = 10 * 1024 * 1024  # 10MB
        
    async def validate_request_size(self, request: Request):
        """Validate request size"""
        content_length = request.headers.get('content-length')
        if content_length and int(content_length) > self.max_request_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Request too large"
            )
    
    def validate_headers(self, request: Request):
        """Validate request headers"""
        # Check for required headers
        user_agent = request.headers.get('user-agent', '')
        if not user_agent or len(user_agent) > 500:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid User-Agent header"
            )


def create_hmac_signature(data: str, secret: str) -> str:
    """Create HMAC signature for data integrity"""
    return hmac.new(
        secret.encode('utf-8'),
        data.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()


def verify_hmac_signature(data: str, signature: str, secret: str) -> bool:
    """Verify HMAC signature"""
    expected = create_hmac_signature(data, secret)
    return hmac.compare_digest(expected, signature)


def hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
    """Hash password with salt"""
    if salt is None:
        salt = hashlib.sha256(str(time.time()).encode()).hexdigest()[:16]
    
    hashed = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return hashed.hex(), salt


def verify_password(password: str, hashed: str, salt: str) -> bool:
    """Verify password against hash"""
    new_hash, _ = hash_password(password, salt)
    return hmac.compare_digest(new_hash, hashed)


# Global instances
security_validator = SecurityValidator()
request_validator = RequestValidator()
ip_whitelist = IPWhitelist()


# Rate limiting decorators
def rate_limit_auth(max_attempts: int = 5, window: int = 300):
    """Rate limit for authentication endpoints"""
    return limiter.limit(f"{max_attempts}/{window}seconds")


def rate_limit_api(max_requests: int = 100, window: int = 60):
    """Rate limit for API endpoints"""
    return limiter.limit(f"{max_requests}/{window}seconds")