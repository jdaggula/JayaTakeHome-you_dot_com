class CustomError(Exception):
    """
    Base class for custom exceptions
    """
    def __init__(self, message, status_code=400, err_code=None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = err_code

class NotFoundError(CustomError):
    """Exception raised for resource not found."""
    def __init__(self, message="Resource not found", status_code=400):
        super().__init__(message, status_code)

class ValidationError(CustomError):
    """Exception raised for validation errors"""
    def __init__(self, message="Invalid request", status_code=400):
        super().__init__(message,status_code)

class InternalError(CustomError):
    """Exception raised for internal errors"""
    def __init__(self, message="Internal error", status_code=400):
        super().__init__(message,status_code)
