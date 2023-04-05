from django.contrib import admin
from .models import ProfileUser, Post, Comment, Follower, SecondaryComment
from django.contrib.auth.models import User
# Register your models here.
admin.site.register(ProfileUser)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Follower)
admin.site.register(SecondaryComment)
class AdminBlog(admin.AdminSite):
    index_title = 'Blog page'
    site_header = 'Blog Website'
    
blog_site = AdminBlog(name='blog')
