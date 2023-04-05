from django.db import models
from base.models import ProfileUser
from django.contrib.auth.models import User
import uuid
from django.utils import timezone
# Create your models here.
class Message(models.Model):
    user = models.ForeignKey(ProfileUser, on_delete=models.CASCADE, related_name='chat_messages')
    recipent = models.ForeignKey(ProfileUser, on_delete=models.CASCADE, related_name='chat_message_recipent')
    group_name = models.TextField()
    description = models.CharField(max_length=2000)
    created = models.DateTimeField(default=timezone.now)
    class Meta:
        ordering = ['created',]
    def __str__(self):
        return self.description[:30]
    def recent_messages():
        return Message.objects.order_by('-created').all()[:30]


class ChatGroupMessage(models.Model):
    users = models.ManyToManyField(ProfileUser, related_name='chat_groups')
    admin = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
