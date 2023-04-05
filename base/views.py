from django.shortcuts import (render, get_object_or_404, redirect,
                              HttpResponseRedirect, HttpResponse)
from django.views.generic import (ListView, TemplateView, DetailView,
                                  UpdateView, CreateView, DeleteView)
from .forms import CommentForm, PostForm
from .models import ProfileUser, Follower, Comment, Post, SecondaryComment
from django.urls import reverse
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponseForbidden
from django.forms.models import model_to_dict
import json
from validate_email import validate_email
from itertools import chain
import re
import os
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from django.core.mail import send_mail
from base.serializers import SearchCommentSerializers, SearchPostSerializers, SearchProfileUsersSerializers
# Create your views here.
# The home page view
class PostList(ListView):
    template_name = 'base/post_list.html'
    context_object_name = 'posts'
    model = Post
    
    def get_queryset(self):
        object_list = self.model.objects.all()
        return object_list
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['totalPost'] = self.get_queryset().count()
        context['page'] = 1
        return context

# The comment section, displaying the details about the post
class PostDetail(LoginRequiredMixin, DetailView):
    login_url = 'basic_app:login'
    model = Post
    context_object_name = 'post'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['item'] = self.model.comments
        return context
    
    # This is to update the post
class PostUpdate(LoginRequiredMixin, UpdateView):
    login_url = 'basic_app:login'
    model = Post
    context_object_name = 'post'
    form_class = PostForm
    def dispatch(self, *args, **kwargs):
        post = self.get_object()
        
        if self.request.user == post.username:
            return super().dispatch( *args, **kwargs)
        else:
            return render(self.request, 'unauthorized.html', status=403)

    def get_success_url(self):
        return reverse('basic_app:post', kwargs={'pk': self.object.pk})
# This is a code that helps delete the post
class PostDelete(LoginRequiredMixin, DeleteView):
    model = Post
    login_url = 'basic_app:login'
    context_object_name = 'post'
    success_url = '/'
# Used dispatch to help know if the user of the post belongs to the request.user(the logged in user) 
    def dispatch(self, *args, **kwargs):
        post = self.get_object()
        if self.request.user == post.username:
            return super().dispatch( *args, **kwargs)
        else:
            return render(self.request, 'unauthorized.html', status=403)

    
# This helps to approve a comment
@login_required(login_url='basic_app:login')
def approveComment(request, pk):
    comment = get_object_or_404(Comment, id=pk)
    post = comment.post
    comment.approve()
    return redirect('basic_app:post', pk=post.id)

@login_required(login_url='basic_app:login')
def unapproveComment(request, pk):
    comment = get_object_or_404(Comment, pk)
    if request.method == 'POST':
        comment.delete()
        comment.save()
        return HttpResponseRedirect(reverse('basic_app:post', args=[comment.post.id]))
    
# This helps to delete a comment, if and only if the the request.user(user logged in) is the same as the user who commented
# @login_required(login_url='basic_app:login')
# def deleteComment(request, pk, pd):
#     post = Post(id=pd)
#     comment = get_object_or_404(Comment, id = pk)
#     if request.user == post.username:
#         if request.method == 'POST':
#             comment.delete()
#             comment.save()
#             return render('/')
#     else:
#         return HttpResponse("You can't access this page")
# This helps save comment to a post
@login_required(login_url='basic_app:login')
def comment(request, pk):
    post = get_object_or_404(Post, id=pk)
    form = CommentForm
    if request.method == 'POST':
        post_comment = request.POST.get('comment')
        form = CommentForm(request.POST)
        if len(post_comment.strip()) > 0:
            if form.is_valid():
                comment = form.save(commit=False)
                comment.post = post
                comment.username = request.user
                comment.save()
                return HttpResponseRedirect(reverse('basic_app:post', args=[pk]))
        else:
            return HttpResponseRedirect(reverse('basic_app:post', args=[pk]))
    return HttpResponseRedirect(reverse('basic_app:post', args=[pk]))
# It helps delete a comment
@login_required(login_url='basic_app:login')
def deleteComment(request, post, pk):
    comment = Comment.objects.get(id=pk)
    if request.method == 'POST':
        if request.user == comment.username:
            comment.delete()
            return HttpResponseRedirect(reverse('basic_app:post', args=[post]))

        else:
            return render(request, 'unauthorized.html', status=403)
    return HttpResponseRedirect(reverse('basic_app:post', args=[post]))


from django import forms
@login_required(login_url='basic_app:login')
def editComment(request, post, pk):
    comment = Comment.objects.get(id=pk)
    commentform = CommentForm(instance=comment)
    error = ''
    if request.method == 'POST':
        if request.user == comment.username:
            commentform = CommentForm(request.POST, instance=comment)
            if commentform.is_valid():
                commentform.save()
                return HttpResponseRedirect(reverse('basic_app:post', args=[post]))      

        else:
            return render(request, 'unauthorized.html', status=403)
    return render(request, 'base/comment_edit.html', {'form': commentform, 'error': commentform.errors.get('comment')})    
# @login_required(login_url='basic_app:login')
# def createPostValidate(request):
#     json = json.loads()
#     data = json['post']
#     if len(str(data).strip()) < 0:
#         return JsonResponse({'error': 'Please insert a value'})
    
@login_required(login_url='basic_app:login')
def createPost(request):
    post = Post
    if request.method == 'POST':
        username = request.user
        description = request.POST['description']
        if  len(str(description).strip()) > 0:
            post = Post.objects.create(username=username, description=description)
            post.save()
        if len(str(description).strip()) == 0 and request.FILES.get('profile_image') is not None:
            post = Post.objects.create(username=username, description='')
            post.pic = request.FILES.get('profile_image')
            post.save() 
        if request.FILES.get('profile_image') != None:
            post.pic = request.FILES.get('profile_image')
            post.save()        
        else:
            messages.info(request, 'Please type in a value')
    return HttpResponseRedirect(reverse('basic_app:home'))

def loginPage(request):
    user = User
    next = request.GET.get('next') if  request.GET.get('next') is not None else ''
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                user_profile_url = '/profile/' + str(username) + '/'     
                if 'profile/AnonymousUser/' in next:
                    next = user_profile_url
                    print('yeahhh i am here ')
                login(request, user)
                if next != '':
                    return HttpResponseRedirect(next)

                else:
                    return HttpResponseRedirect(reverse('basic_app:profile', args=[user.username]))
                    
        else:
            messages.info(request, 'Invalid Cresidentials, try again')

    return render(request, 'login.html')

@login_required(login_url='basic_app:login')
def logoutPage(request):
    logout(request)
    return redirect('basic_app:home')

def validateUsername(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data['username']
        if not str(username).isalnum():
            return JsonResponse({"error": 'Please ensure that your username contains only alphanumerics'}, status=400)
        if User.objects.filter(username=username).exists():
            return JsonResponse({'error': 'This user already exists'}, status=400)
        else:
            return JsonResponse({'status': True})
        
def validateUserEmail(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data['email']
        if not validate_email(email):
            return JsonResponse({'error': 'Invalid email'}, status=400)
        if User.objects.filter(email=email).exists():
            return JsonResponse({'error': 'This email is already in use'}, status=400)
        else:
            return JsonResponse({'status': True})
        
def validatePassword(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        password = data['password']
        if len(str(password).strip()) < 7:
            return JsonResponse({'error': 'Please ensure that your password has a minimum length of 7'}, status=400)
        if not re.search(r'[a-z]', password):
           return JsonResponse({'error': 'Please ensure that your password contains lowecase letters for security reason'}, status=400)
        if not re.search(r'[A-Z]', password):
            return JsonResponse({'error': 'Please ensure that your password contains uppercase letters for security reason'}, status=400)
        else:
            return JsonResponse({'status': True})
        
def validateConfirmPassword(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        confirm_password = data['confirmPassword']
        password = data['password']
        if len(password) < 7:
            return JsonResponse({'error': 'Please ensure that your password has a minimum length of 7'}, status=400)
        if not re.search(r'[a-z]', password):
           return JsonResponse({'error': 'Please ensure that your password contains lowercase letters for security reason'}, status=400)
        if not re.search(r'[A-Z]', password):
            return JsonResponse({'error': 'Please ensure that your password contains uppercase letters for security reason'}, status=400)
        if confirm_password != password:
            return JsonResponse({'error': 'Ensure that both passwords are the same'}, status=400)
        else:
            return JsonResponse({'status': True})
        
def register(request):
    if request.method == 'POST':
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirmPassword = request.POST.get('confirm_password')
        email = request.POST.get('email')
        
        if not str(username).isalnum():
            return redirect('basic_app:register')
        if not re.search(r'[a-z]', password):
            return redirect('basic_app:register')
        if not re.search(r'[A-Z]', password):
            return redirect('basic_app:register') 
        if not validate_email(email):
            return redirect('basic_app:register') 
        if User.objects.filter(username=username).exists():
            return redirect('basic_app:register')
        if User.objects.filter(email=email).exists():
            return redirect('basic_app:register') 
        if len(str(password).strip()) > 7:
            if password == confirmPassword:
                user = User.objects.create_user(username=username, email=email, first_name=firstname, last_name=lastname)
                user.save()
                user.set_password(password)
                user.save()                
                return redirect('basic_app:login')
            else:
                return redirect('basic_app:register')            
        else:
            return redirect('basic_app:register')
        
    return render(request, 'signup.html')

@login_required(login_url='basic_app:login')
def profile(request, pk):
    user = User.objects.get(username=pk)
    follow_bool = False
    profile = ProfileUser.objects.get(user=user)
    follower = Follower.objects.filter(follow_user = profile.user)
    total_user_following = Follower.objects.filter(user_followed=profile.user)
    profile_page = 'home'
    followers_object = []
    it = []

    for i in follower.exclude(user_followed=profile.user):

        followers_object.append(ProfileUser.objects.filter(user=i.user_followed))

    follower_obj = list(chain(*followers_object))
    follower_obj_deduced = list(chain(*followers_object))[0:6]
    follower_obj_remaining = f'and {len(follower_obj_deduced) - 6} more' if  len(follower_obj_deduced) / 6 > 1 else False
    if Follower.objects.filter(follow_user=profile.user, user_followed=request.user).exists():
        follow_bool = False
    else:
        follow_bool = True
    total_followers = follower.count()
    post = user.post
    total_posts = post.count()
    page = 4
    data = {'profile': profile,
            'post': post, 'total_posts': total_posts, 'page': page,
            "follower": follower, 'total_follower': total_followers,
            'follow_bool': follow_bool,
            'total_following': total_user_following.count(), 'followers_profile': follower_obj_deduced,
            'follower_obj_remaining':follower_obj_remaining, 'profile_page': profile_page}
    return render(request, 'base/profile.html', context=data)

@login_required(login_url='basic_app:login')
def like_post(request, pk):
    post = get_object_or_404(Post, id=pk)
    if request.method == 'POST':
        if post.likes.filter(username=request.user.username).exists():
            post.likes.remove(request.user)
        else:
            post.likes.add(request.user)
    return HttpResponseRedirect(reverse('basic_app:post', args=[pk]))


@login_required(login_url='basic_app:login')
def settings(request):
    page = 5
    profile = get_object_or_404(ProfileUser, user=request.user)
    if profile.user == request.user:
        if request.method == 'POST':
            username = request.POST.get('username')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            bio = request.POST.get('bio')
            email = request.POST.get('email')
            location = request.POST.get('location')
            
            profile.bio = bio
            profile.user.first_name = first_name
            profile.user.last_name = last_name
            profile.user.email = email
            profile.user.username = username
            profile.location = location
            profile.save()
            profile.user.save()
            if request.FILES.get('image') is not None:
                image = request.FILES.get('image')
                profile.profile_image = image
                profile.save()
            if request.POST.get('checkbox') == 'on':
                profile.profile_image.delete()
                profile.save()
    return render(request, 'settings.html', {'profile': profile, 'page': page})

@login_required(login_url='basic_app:login')
def followUser(request, pk):
    profile = get_object_or_404(ProfileUser, id=pk)
    follower = Follower
        
    if request.method == 'POST':
        if Follower.objects.filter(follow_user=profile.user, user_followed=request.user).exists():
            Follower.objects.filter(follow_user=profile.user, user_followed=request.user).delete()
        else:
            follower = Follower(follow_user=profile.user, user_followed=request.user)
            follower.save()
        
    return HttpResponseRedirect(reverse('basic_app:profile', args=[profile.user]))

@login_required(login_url='basic_app:login')
def aboutPage(request, pk):
    #     profile = get_object_or_404(ProfileUser, id=pk)
    follower = Follower
    if request.method == 'POST':
        if Follower.objects.filter(follow_user=profile.user, user_followed=request.user).exists():
            Follower.objects.filter(follow_user=profile.user, user_followed=request.user).delete()
        else:
            follower = Follower(follow_user=profile.user, user_followed=request.user)
            follower.save()
        
    return HttpResponseRedirect(reverse('basic_app:profile', args=[profile.user]))

@login_required(login_url='basic_app:login')
def aboutPage(request, pk):
    profile = ProfileUser.objects.get(id=pk)
    follower = Follower.objects.filter(follow_user = profile.user)
    user = profile.user
    total_user_following = Follower.objects.filter(user_followed=profile.user)
    follow_bool = True
    total_followers = follower.count()
    post = user.post
    total_posts = post.count()
    profile_page = 'about'
    page = 4
    if Follower.objects.filter(follow_user=profile.user, user_followed=request.user).exists():
        follow_bool = False
    else:
        follow_bool = True
    return render(request, 'base/about.html', {'profile': profile,
                                                 'post': post, 'total_posts': total_posts, 'page': page,
                                                 "follower": follower, 'total_follower': total_followers,
                                                 'follow_bool': follow_bool,
                                                 'total_following': total_user_following.count(), 'profile_page': profile_page})


@login_required(login_url='basic_app:login')
def jsonPage(request):
    followers =Follower.objects.filter(follow_user=request.user)
    data = list(followers.values())
    # data = model_to_dict(followers)
    # json_data = json.dumps(data)
    json_data = [{'id': follower.id,'follow_user': follower.follow_user.username,
                  'follow_user_id': follower.follow_user.id, 'user_followed': follower.user_followed.username,
                  'user_followed_id': follower.user_followed.id,} for follower in followers]
    return JsonResponse(json_data, safe=False)
from rest_framework import permissions, serializers, generics
from base import serializers
class jsonFollowers(generics.ListCreateAPIView):
    serializer_class = serializers.FollowerSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        queryset = Follower.objects.filter(follow_user=self.request.user)
        return queryset
    

def likeComment(request, pk, ck):
    comment = get_object_or_404(Comment, id=ck)
    if request.method == 'POST':
        if comment.likes.filter(username=request.user).exists():  
            comment.likes.remove(request.user)
        else:
            comment.likes.add(request.user)
    return HttpResponseRedirect(reverse('basic_app:post', args=[pk]))
    
def bootstrap(request):
    return render(request, 'base/bootstrap.html')

def profilePosts(request, pk):
    profile = ProfileUser.objects.get(id=pk)
    post = Post.objects.filter(username=profile.user)
    
    follower = Follower.objects.filter(follow_user = profile.user)
    user = profile.user
    total_user_following = Follower.objects.filter(user_followed=profile.user)
    follow_bool = True
    total_followers = follower.count()
    page = 'posts'
    if Follower.objects.filter(follow_user=profile.user, user_followed=request.user).exists():
        follow_bool = False
    else:
        follow_bool = True
    total_posts = post.count()
    page = 4
    profile_page = 'posts'

    return render(request, 'base/profile_posts.html',
                 {'profile': profile,
                'total_posts': total_posts, 'page': page,
                "follower": follower, 'total_follower': total_followers,
                'follow_bool': follow_bool,
                'total_following': total_user_following.count(), 'post': post, 'profile_page': profile_page})

def profile_followers(request, pk):
    profile = ProfileUser.objects.get(id=pk)
    post = Post.objects.filter(username=profile.user)
    follower = Follower.objects.filter(follow_user = profile.user)
    total_user_following = Follower.objects.filter(user_followed=profile.user)
    profile_page = 'home'
    followers_object = []
    for i in follower:
        followers_object.append(ProfileUser.objects.filter(user=i.user_followed))
    follower_obj = list(chain(*followers_object))
    follower = Follower.objects.filter(follow_user = profile.user)
    user = profile.user
    total_user_following = Follower.objects.filter(user_followed=profile.user)
    follow_bool = True
    if Follower.objects.filter(follow_user=profile.user, user_followed=request.user).exists():
        follow_bool = False
    else:
        follow_bool = True
    total_followers = follower.count()
    page = 'posts'
    total_posts = post.count()
    page = 4
    profile_page = 'followers'

    return render(request, 
                        'base/profile_followers.html', {'profile': profile,
                        'total_posts': total_posts, 'page': page,
                        "follower": follower, 'total_follower': total_followers,
                        'follow_bool': follow_bool,
                        'total_following': total_user_following.count(),
                        'followers_profile': follower_obj, 'post': post, 'profile_page': profile_page})

def get_user_followed(request, pk):
    profile = ProfileUser.objects.get(id=pk)
    post = Post.objects.filter(username=profile.user)
    follower = Follower.objects.filter(user_followed = profile.user)
    total_user_following = Follower.objects.filter(user_followed=profile.user)
    profile_page = 'user_followed'
    followers_object = []
    for i in follower:
        followers_object.append(ProfileUser.objects.filter(user=i.user_followed))
    follower_obj = list(chain(*followers_object))
    follower = Follower.objects.filter(follow_user = profile.user)
    user = profile.user
    total_user_following = Follower.objects.filter(user_followed=profile.user)
    follow_bool = True
    total_followers = follower.count()
    total_posts = post.count()
    page = 4
    profile_page = 'followers'

    return render(request, 'base/profile_followed.html', {'profile': profile,
                                                 'total_posts': total_posts, 'page': page,
                                                 "follower": follower, 'total_follower': total_followers,
                                                 'follow_bool': follow_bool,
                                                 'total_following': total_user_following.count(),'followers_profile': follower_obj, 'post': post, 'profile_page': profile_page})
def add_secondary_comment(request, pk):
    comment = Comment.objects.get(id=pk)
    post = comment.post
    # get_comment = SecondaryComment
    if request.method == 'POST':
        secondary_comment = request.POST.get('secondary_comment')
        get_comment = SecondaryComment.objects.create(user=request.user, comment=comment, secondary=secondary_comment)
        try:
            get_comment.save()
            return HttpResponseRedirect(reverse('basic_app:post', args=[post.id]))
        except:
            return HttpResponse('Error in cod')
    return HttpResponseRedirect(reverse('basic_app:post', args=[post.id]))
def secondary_comment_page(request, pk):
    secondary_comment = SecondaryComment(id=pk)
    filter_sec = SecondaryComment.objects.filter(comment=comment)
    return render(request, 'seondary_comment.html')

def notification_page(request):
    return(render, 'ind.html')

def search_post_datas(query):
    dic = {}
    user = User.objects.get(username=query) if User.objects.filter(username=query).exists() else None
    
    post_username_data = Post.objects.filter(username=user) if Post.objects.filter(username=user).exists() or user is not None else {}
    post = Post.objects.filter(Q(description__icontains=query))
    
    dic['posts_data'] = list(post.values('id', 'username', 'description')) if len(post) > 0 else {}
    dic['posts_data_usernames'] = list(post_username_data.values('id', 'username', 'description')) if len(post_username_data) > 0 else []
    return dic

def search_profile_datas(query):
    dic = {}
    user = User.objects.get(username=query) if User.objects.filter(username=query).exists() else None
    profiles = ProfileUser.objects.filter(user=user) if ProfileUser.objects.filter(user=user).exists() or user is not None else {}

    
    dic['profiles'] = list(profiles.values('id', 'user', 'profile_image')) if len(profiles) > 0 else {}

    return dic
def search(request):
    
    if request.method == 'GET':
        results = {}
        
        query = request.GET.get('search') if request.GET.get('search') else ''
        page=6
        post_data = search_post_datas(query=query)
        profile_data = search_profile_datas(query)
        arr = []
        results['posts'] = post_data
        results['profiles'] = profile_data
        arr.append(results)
    return render(request, 'searchpage.html')

def index(request):
    return render(request, "base/lobby.html")
from rest_framework.response import Response
from django.core import serializers

class searchPage(APIView):
    def get(self, request):
        post = Post.objects.all()
        dic = {}
        res = {'posts': list(post.values('id', 'username', 'description'))}
        return JsonResponse(res, safe=False)
        data = SearchPostSerializers(dic, many=True).data

        return Response(data)