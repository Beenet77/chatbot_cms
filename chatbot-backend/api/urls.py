from django.urls import path
from .views import GetCMSContentView, HandleChatView

urlpatterns = [
    path('cms/<str:language>/<str:key>/', GetCMSContentView.as_view(), name='cms-content'),
    path('chat/', HandleChatView.as_view(), name='chat'),
]
