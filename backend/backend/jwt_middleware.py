from rest_framework_simplejwt.tokens import UntypedToken, AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

User = get_user_model()

@database_sync_to_async
def get_user(token):
    try:
        UntypedToken(token)
        access_token = AccessToken(token)
        user_id = access_token['user_id']
        return User.objects.get(id=user_id)
    except (TokenError, InvalidToken, User.DoesNotExist, Exception):
        return None

