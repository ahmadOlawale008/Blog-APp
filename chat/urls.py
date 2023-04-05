from django.urls import re_path, path
from chat import views

app_name = 'chat_app'
urlpatterns = [
    path('', views.chatPage, name='chatroom'),
    path('chatpage/<str:room_id>/', views.chatmsg, name='chat_msg'),
]