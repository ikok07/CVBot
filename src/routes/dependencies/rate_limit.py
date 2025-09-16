import time

from starlette import status
from starlette.requests import Request

from src.models.app_state import app_state
from src.models.errors.api import APIError

def rate_limit(limit: int, window_seconds: int):
    def dependency(request: Request):
        ip_addr = request.client.host
        user_agent = request.headers.get("user-agent", "unknown")

        key = f"{ip_addr}:{user_agent}:{int(time.time() // window_seconds)}"

        req_count = app_state.redis_store.incr(key, 1)
        
        if req_count is None:
            raise APIError(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, message="Unknown error occurred!")

        if req_count == 1:
            app_state.redis_store.expire(key, window_seconds)

        if req_count > limit:
            raise APIError(status_code=status.HTTP_429_TOO_MANY_REQUESTS, message="User Rate Limit Exceeded")

    return dependency