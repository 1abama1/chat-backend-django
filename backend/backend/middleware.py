from urllib.parse import parse_qs
from .jwt_middleware import get_user

class JwtAuthMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        query = parse_qs(scope["query_string"].decode())
        token = query.get("token")
        scope["user"] = await get_user(token[0]) if token else None
        return await self.app(scope, receive, send)

