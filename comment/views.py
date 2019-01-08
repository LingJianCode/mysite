from django.shortcuts import render,redirect
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from .models import Comment
from .forms import CommentForm


def update_comment(request):
    referer = request.META.get('HTTP_REFERER', reverse('home'))
    #传入user来处理user验证问题
    comment_form = CommentForm(request.POST, user=request.user)
    if comment_form.is_valid():
        comment = Comment()
        comment.user = comment_form.cleaned_data['user']
        comment.text = comment_form.cleaned_data['text']
        comment.content_object = comment_form.cleaned_data['model_obj']
        comment.save()
        return redirect(referer)
    else:
        return render(request, 'error.html', {'message':'评论异常',"back_url":referer})

