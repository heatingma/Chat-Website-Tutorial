
from django.urls import path
from chat import views

urlpatterns = [
    path('my/', views.my, name='my'),
    path('settings/', views.settings, name='settings'),
    path('chatroom/', views.chatroom, name='chatroom'),
    path('chatroom/<str:room_name>/<str:post_name>/', views.innerroom, name='innerroom'),
]
