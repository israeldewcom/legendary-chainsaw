class TaxFlowError(Exception):
    """Base exception for all application errors."""
    def __init__(self, message: str, code: str = "taxflow_error", status_code: int = 400):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(TaxFlowError):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, code="not_found", status_code=404)


class UnauthorizedError(TaxFlowError):
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message, code="unauthorized", status_code=401)


class ForbiddenError(TaxFlowError):
    def __init__(self, message: str = "Forbidden"):
        super().__init__(message, code="forbidden", status_code=403)


class BusinessError(TaxFlowError):
    def __init__(self, message: str):
        super().__init__(message, code="business_error", status_code=400)


class ValidationError(TaxFlowError):
    def __init__(self, message: str):
        super().__init__(message, code="validation_error", status_code=422)


class RateLimitExceededError(TaxFlowError):
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, code="rate_limit_exceeded", status_code=429)


class SubscriptionLimitError(TaxFlowError):
    def __init__(self, message: str = "Subscription limit reached"):
        super().__init__(message, code="subscription_limit", status_code=403)


class IdempotencyError(TaxFlowError):
    def __init__(self, message: str = "Idempotency key already used"):
        super().__init__(message, code="idempotency_error", status_code=409)


class WebhookProcessingError(TaxFlowError):
    def __init__(self, message: str = "Webhook processing failed"):
        super().__init__(message, code="webhook_error", status_code=500)


class ConflictError(TaxFlowError):
    def __init__(self, message: str = "Conflict with existing resource"):
        super().__init__(message, code="conflict", status_code=409)


class ServiceUnavailableError(TaxFlowError):
    def __init__(self, message: str = "Service temporarily unavailable"):
        super().__init__(message, code="service_unavailable", status_code=503)
