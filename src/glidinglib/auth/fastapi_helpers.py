from typing import Any, Callable, Optional
from glidinglib.auth.auth_service import GlidingAppAuthService
from glidinglib.auth.user_context import UserContext


def get_current_user_from_request(
    request: Any,
    auth_service: GlidingAppAuthService,
    dev_fallback_email: str = "local_dev@cgc.org.uk",
) -> UserContext:
    """
    Extracts the authenticated user's email from request headers and returns their UserContext.
    Falls back to dev_fallback_email when running on localhost.
    """
    headers = getattr(request, "headers", {})
    email = auth_service.extract_email_from_headers(headers)

    # Local dev fallback when accessed directly on localhost without headers
    if not email:
        client_host = request.client.host if getattr(request, "client", None) else ""
        if client_host in ("127.0.0.1", "localhost"):
            email = dev_fallback_email

    return auth_service.get_user_context(email)


def create_user_dependency(
    auth_service: GlidingAppAuthService,
    dev_fallback_email: str = "local_dev@cgc.org.uk",
) -> Callable[[Any], UserContext]:
    """
    Creates a FastAPI Depends compatible callable that yields the current UserContext.
    """
    def dependency(request: Any) -> UserContext:
        return get_current_user_from_request(request, auth_service, dev_fallback_email)

    return dependency
