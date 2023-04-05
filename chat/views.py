from django.shortcuts import render
from django.http import HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from base.models import Post, Follower
from django.contrib.auth.models import User
from django.db.models import Q
from chat.models import Message
from base.models import ProfileUser
# Create your views here.
@login_required(login_url='basic_app:login')
def chatPage(request):
    profileusers = ProfileUser.objects.exclude(user=request.user)
    users = User.objects.exclude(username=request.user.username)
    return render(request, 'chat/chatgroup.html', { 'users': users, 'profiles': profileusers})

@login_required(login_url='basic_app:login')
def chatmsg(request, room_id):
    users = User.objects.exclude(username=request.user.username)
    user = request.user
    other_profile = ProfileUser.objects.get(id=room_id)
    print(user.profile.id, other_profile.id)
    if other_profile.id == user.profile.id:
        return HttpResponseBadRequest('Bad Request')


    other_profile_user = User.objects.get(username=other_profile.user.username)
    return render(request, 'chat/chatpage.html', {'room_name': other_profile_user.username, 'other_profile_user': other_profile_user, 'username': user.username, 'user': user,'users': users, 'room_id': room_id})