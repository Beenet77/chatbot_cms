from django.urls import path
from .views import GetCMSContentView, HandleChatView,LogoView,HandleChatUser

urlpatterns = [
    path('cms/<str:language>/<str:key>/', GetCMSContentView.as_view(), name='cms-content'),
    path('chat/', HandleChatView.as_view(), name='chat'),
    path('chat/user/', HandleChatUser.as_view(), name='chat_user'),
    path('logo/', LogoView.as_view(), name='logo'),
]
