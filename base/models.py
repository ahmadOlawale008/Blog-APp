from django.db import models
from django.contrib.auth.models import User
import uuid
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.

class ProfileUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    id = models.UUIDField(primary_key= True, default=uuid.uuid4)
    profile_image = models.ImageField(upload_to='profile_img', default='account_circle_FILL0_wght400_GRAD0_opsz48.svg')
    bio = models.TextField(max_length=120, blank=True, null=True)
    location = models.CharField(max_length=200, blank=True)

    @receiver(post_save, sender=User)
    def create_profile(sender, instance, created, **kwargs):
        if created:
            ProfileUser.objects.create(user=instance)
            print(sender, created, instance)
    @receiver(post_save, sender=User)
    def save_profile(sender, instance, **kwargs):
        print(sender, instance)
        instance.profile.save()
    def __str__(self):
        return self.user.username
    
class Follower(models.Model):
    follow_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
    user_followed = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following', null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    username = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post')
    pic = models.ImageField(upload_to='img', blank=True)
    tag = models.ManyToManyField(User, related_name='post_tag', blank=True)
    likes = models.ManyToManyField(User, related_name='liked_post', blank=True)
    date_posted = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    description = models.CharField(max_length=600)
    post_approved = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-date_updated', '-date_posted']
    
    def __str__(self):
        return self.description
    def total_likes(self):
        return self.likes.count()
    def approve_posts(self):
        self.post_approved = True
        self.save()

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    username = models.ForeignKey(User, related_name='user_details', on_delete=models.CASCADE)
    comment = models.CharField(max_length=2225)
    comment_posted = models.DateTimeField(auto_now_add=True)
    comment_updated = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(User, related_name='liked', blank=True)
    commment_approved = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-comment_updated', '-comment_posted'] 
        
    def user_usernames(self):
        return self.username.username
    def total_likes(self):
        return self.likes.count()
    def approve(self):
        self.commment_approved = True
        self.save()
    def __str__(self):
        return self.comment[0:30]
    
class SecondaryComment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='secondary')
    secondary = models.CharField(max_length=1000)
    secondary_comment_created = models.DateTimeField(auto_now=True)
    secondary_comment_updated = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.secondary[:30]