from rest_framework import serializers
from base.models import Follower, Post, Comment, ProfileUser
class FollowerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follower
        fields = ('id', 'follow_user', 'user_followed')
class SearchPostSerializers(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('id',)

class SearchCommentSerializers(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'
class SearchProfileUsersSerializers(serializers.ModelSerializer):
    class Meta:
        model = ProfileUser
        fields = '__all__'