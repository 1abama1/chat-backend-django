from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from chats.views import ChatViewSet
from chat_messages.views import ChatMessageViewSet, MessageViewSet, PinnedMessageViewSet
from users.views import UserViewSet

router = DefaultRouter()
router.register('chats', ChatViewSet, basename='chat')
router.register('messages', MessageViewSet, basename='message')
router.register('pinned', PinnedMessageViewSet, basename='pinned')
router.register('users', UserViewSet, basename='user')

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/auth/', include('users.urls')),
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('api/', include(router.urls)),
    
    path(
        'api/chats/<int:chat_id>/messages/',
        ChatMessageViewSet.as_view({
            'get': 'list',
            'post': 'create',
        }),
        name='chat-messages'
    ),

    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
