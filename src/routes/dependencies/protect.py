import asyncio
import os

from clerk_backend_api import AuthenticateRequestOptions, Clerk, User
from clerk_backend_api.security import AuthStatus
from starlette import status
from starlette.requests import Request
from tortoise.exceptions import DoesNotExist

from src.models.db.profiles import Profile
from src.models.errors.api import APIError

async def protect_dependency(request: Request) -> (User, Profile):
    sdk = Clerk(bearer_auth=os.getenv("CLERK_SECRET_KEY"))
    print("Initializing Clerk...")
    def auth():
        state = sdk.authenticate_request(
            request=request,
            options=AuthenticateRequestOptions()
        )
        print("Clerk authentication finished")
        print(state)
        if state.status == AuthStatus.SIGNED_IN:
            user = sdk.users.get(user_id=state.payload["sub"])
            print("Clerk user checked")
            print(user)
            if not user:
                raise APIError(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, message="User not found")
            return user
        else:
            raise APIError(status_code=status.HTTP_401_UNAUTHORIZED, message="Unauthorized")

    clerk_user = await asyncio.to_thread(auth)
    print("Fetching profile from db...")
    try:
        profile = await Profile.get(id=clerk_user.id)
        return clerk_user, profile
    except DoesNotExist as e:
        print("User profile does not exist!")
    raise APIError(status_code=status.HTTP_401_UNAUTHORIZED, message="Unauthorized")