from django import forms
from .models import ProfileUser, Follower, Comment, Post
from django.contrib.auth.models import User
from django.forms import ValidationError
class PostForm(forms.ModelForm):
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'post-descriotion'}))
    pic = forms.ImageField(required=False)
    tag = forms.ModelMultipleChoiceField(queryset=User.objects.all(), required= False)
    class Meta:
        model = Post
        fields = ('description', 'pic', 'tag')
        
class CommentForm(forms.ModelForm):
    def validate_comment(self):
        comment = self.cleaned_data['comment']
    comment = forms.CharField(widget=forms.Textarea(attrs={'class': 'comment-edit form-control'}), error_messages={'required': 'Please ensure that your text has a minimum length of 1'}, required=True)

    class Meta:
        model = Comment
        fields = ('comment',)
        