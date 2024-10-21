class MarvelAPIException(Exception):
    """Base class for all Marvel API exceptions."""
    def __init__(self, message):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return f"MarvelAPIException: {self.message}"

class MarvelAPIAuthenticationError(MarvelAPIException):
    """Exception raised for authentication errors (e.g., invalid API keys)."""
    def __init__(self, message="Authentication failed. Please check your API keys."):
        super().__init__(message)

class MarvelAPIDataError(MarvelAPIException):
    """Exception raised for data retrieval errors from the Marvel API."""
    def __init__(self, message="Error retrieving data from the Marvel API."):
        super().__init__(message)

class MarvelAPIResourceNotFound(MarvelAPIException):
    """Exception raised when a resource is not found (404 error)."""
    def __init__(self, message="The requested resource was not found."):
        super().__init__(message)

class MarvelAPIRateLimitExceeded(MarvelAPIException):
    """Exception raised when the API rate limit is exceeded."""
    def __init__(self, message="Rate limit exceeded. Try again later."):
        super().__init__(message)
