import os
from fastapi_users.authentication import JWTAuthentication

SECRET = os.environ.get("APP_SECRET")

jwt_auth = JWTAuthentication(secret=SECRET, lifetime_seconds=3600)
