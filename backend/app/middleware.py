import time
import logging
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from utils.security import request_validator, ip_whitelist


logger = logging.getLogger(__name__)


async def security_middleware(request: Request, call_next):
    """Security middleware for request validation"""
    start_time = time.time()
    
    try:
        # IP whitelist check (if configured)
        client_ip = request.client.host
        if not ip_whitelist.is_allowed(client_ip):
            logger.warning(f"Request from non-whitelisted IP: {client_ip}")
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": "Access denied from this IP address"}
            )
        
        # Request size validation
        await request_validator.validate_request_size(request)
        
        # Header validation
        request_validator.validate_headers(request)
        
        # Add security headers to response
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        
        # Log request
        process_time = time.time() - start_time
        logger.info(
            f"{request.method} {request.url.path} - "
            f"Status: {response.status_code} - "
            f"Time: {process_time:.3f}s - "
            f"IP: {client_ip}"
        )
        
        return response
        
    except HTTPException as e:
        logger.warning(f"Security validation failed: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Security middleware error: [{type(e).__name__}('{str(e)}')]")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal security error"}
        )


async def logging_middleware(request: Request, call_next):
    """Logging middleware for request/response tracking"""
    start_time = time.time()
    
    # Log request
    logger.info(f"Request: {request.method} {request.url}")
    
    # Process request
    response = await call_next(request)
    
    # Log response
    process_time = time.time() - start_time
    logger.info(
        f"Response: {response.status_code} - "
        f"Time: {process_time:.3f}s"
    )
    
    return response