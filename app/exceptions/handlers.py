"""
Global exception handlers for the FastAPI application.

This module contains centralized exception handlers that provide consistent
error responses and logging across the entire application.
"""

import sys
import traceback
from datetime import datetime
from typing import Any, Dict

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.logger import logger
from app.exceptions.base import BaseException
from app.exceptions.api import (
    APIException,
    UnauthorizedException,
    ForbiddenException,
    RateLimitException
)


def unwrap_exception(exc: Exception) -> Exception:
    """Unwrap ExceptionGroup to get the actual exception (Python 3.11+).
    
    In Python 3.11+, exceptions raised in async contexts may be wrapped in
    ExceptionGroup. This function unwraps them to get the actual exception.
    
    Args:
        exc: The exception (possibly wrapped in ExceptionGroup)
        
    Returns:
        The unwrapped exception
    """
    if sys.version_info >= (3, 11):
        if type(exc).__name__ == 'ExceptionGroup':
            if hasattr(exc, 'exceptions') and exc.exceptions:
                return exc.exceptions[0]
    
    return exc


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle validation errors from request data.

    Args:
        request: The request that caused the validation error
        exc: The validation error

    Returns:
        JSONResponse: A formatted error response
    """
    logger.error(
        "validation_error",
        client_host=request.client.host if request.client else "unknown",
        path=request.url.path,
        errors=str(exc.errors()),
    )

    formatted_errors = []
    for error in exc.errors():
        loc = " -> ".join([str(loc_part) for loc_part in error["loc"] if loc_part != "body"])
        formatted_errors.append({"field": loc, "message": error["msg"]})

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Validation error", "errors": formatted_errors},
    )


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle all exceptions with appropriate status codes and messages.
    
    Args:
        request: The request that caused the exception
        exc: The exception
        
    Returns:
        JSONResponse: A formatted error response
    """
    exc = unwrap_exception(exc)
    
    if isinstance(exc, BaseException):
        logger.warning(
            "vpaura_exception",
            error_type=type(exc).__name__,
            error_message=str(exc),
            path=request.url.path,
            method=request.method,
            client_host=request.client.host if request.client else "unknown",
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status": "error",
                "error": exc.code,
                "detail": exc.message,
                "path": request.url.path,
                "timestamp": datetime.now().isoformat(),
            }
        )
    
    error_type = type(exc).__name__
    error_message = str(exc)
    
    logger.error(
        "unhandled_exception",
        error_type=error_type,
        error=error_message,
        path=request.url.path,
        method=request.method,
        client_host=request.client.host if request.client else "unknown",
        traceback=traceback.format_exc(),
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "error": "Internal Server Error",
            "error_type": error_type,
            "detail": error_message,
            "path": request.url.path,
            "timestamp": datetime.now().isoformat(),
        }
    )


def setup_exception_handlers(app) -> None:
    """Set up all exception handlers for the FastAPI application.
    
    Args:
        app: The FastAPI application instance
    """
    if sys.version_info >= (3, 11):
        @app.exception_handler(Exception)
        async def unified_exception_handler(request: Request, exc: Exception):
            """Unified handler that unwraps ExceptionGroup and routes to appropriate handler."""
            unwrapped_exc = unwrap_exception(exc)
            
            if isinstance(unwrapped_exc, RequestValidationError):
                return await validation_exception_handler(request, unwrapped_exc)
            else:
                return await global_exception_handler(request, unwrapped_exc)
    else:
        app.add_exception_handler(RequestValidationError, validation_exception_handler)
        app.add_exception_handler(Exception, global_exception_handler)
