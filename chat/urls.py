
from django.urls import path
from chat.views import chatroom, innerroom, my, settings

urlpatterns = [
    path('my/', my, name='my'),
    path('settings/', settings, name='settings'),
    path('chatroom/', chatroom, name='chatroom'),
    path('chatroom/<str:room_name>/<str:post_name>/', innerroom, name='innerroom'),
]
