from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from jose import JWTError
from app.common.exceptions import TaxFlowError
import structlog

logger = structlog.get_logger()


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning("Validation error", errors=exc.errors(), body=exc.body, path=request.url.path)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "code": "validation_error"},
    )


async def integrity_error_handler(request: Request, exc: IntegrityError):
    logger.exception("Database integrity error", error=str(exc), path=request.url.path)
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": "Data conflict", "code": "integrity_error"},
    )


async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError):
    logger.exception("Database error", error=str(exc), path=request.url.path)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Database error", "code": "database_error"},
    )


async def jwt_error_handler(request: Request, exc: JWTError):
    logger.warning("JWT error", error=str(exc), path=request.url.path)
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": "Invalid authentication credentials", "code": "invalid_token"},
        headers={"WWW-Authenticate": "Bearer"},
    )


async def taxflow_error_handler(request: Request, exc: TaxFlowError):
    logger.info("Business error", error=exc.message, code=exc.code, path=request.url.path)
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message, "code": exc.code},
    )


async def http_exception_handler(request: Request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "code": "http_error"},
    )


async def generic_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception", error=str(exc), path=request.url.path)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal error occurred", "code": "internal_error"},
    )
