from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
import json
from chat.models import Message
from django.contrib.auth.models import User
from base.models import ProfileUser
import unicodedata
class ChatConsumer(WebsocketConsumer):
    def connect(self):
        user = self.scope['user']
        self.user_profile_id = ProfileUser.objects.get(user=user).id
        other_user = self.scope['url_route']['kwargs']['room_name']
        other_user_profile = ProfileUser.objects.get(id=other_user)
        self.other_user_profile_id = other_user_profile.id
        if user.id > other_user_profile.user.id:
            self.room_group_name = f'chat_{self.user_profile_id}-{self.other_user_profile_id}'
        else:
            self.room_group_name = f'chat_{self.other_user_profile_id}-{self.user_profile_id}'
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )
        self.accept()
        self.send(json.dumps({"status": "Online"}))
    def get_messages(self, data):
        messages = Message.objects.filter(group_name=self.room_group_name)
        context = {'command': 'get_message', 'message': self.convert_messages_json(messages=messages)}
        return self.send_chats_msg(context)
    def create_message(self, data):
        author = data['author']
        recipent = data['to']
        user = User.objects.get(username=author)
        recipent_user = User.objects.get(username=recipent)
        profile_user = ProfileUser.objects.get(user=user)
        recipent_profile_user = ProfileUser.objects.get(user=recipent_user)
        description = data['description']
        group_name = self.room_group_name
    
        created_message = Message.objects.create(user=profile_user, recipent=recipent_profile_user, description=description, group_name=group_name)
        content = {'command': 'create_message', 'message': self.convert_message(created_message)}
        self.send_message(data=content)
        
    def convert_messages_json(self, messages):
        message_arr = []
        for message in messages:
            message_arr.append(self.convert_message(message=message))
        return message_arr
    def convert_message(self, message):
        self.author = message.user.user.username
        self.recipent = message.recipent.user.username
        self.group_name = message.group_name
        self.desc = message.description
        self.date_created = str(message.created)
        content = {'author': self.author, 'group_name': self.group_name, 'recipent': self.recipent, 'description': self.desc, 'date_created': self.date_created}
        return content
    def get_command(self, command):
        commads = {'get_message': self.get_messages, 'create_message': self.create_message}
        return commads[command]
    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {"type": "chat_disconnected"}
        )
    def chat_disconnected(self):
        self.send(json.dumps({'status': 'offline', "username": self.recipent}))
        
    def disconnect_chat(self, data):
        self.send(json.dumps({"status": "offline"}))
    
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        command = text_data_json['action']
        command_funct = self.get_command(command=command)
        command_funct(data=text_data_json)
    def send_message(self, data):
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {"type": 'chat_message', 'message': data}
        )
        
    def send_chats_msg(self, message):
        self.send(json.dumps(message))
        
    def send_typing_msg(self, message):
        self.send(json.dumps(message))   
    def chat_message(self, data):
        msg = data['message']
        return self.send(json.dumps(msg))