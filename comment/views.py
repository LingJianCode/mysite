from django.shortcuts import render,redirect
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.http import JsonResponse
from django.utils.timezone import localtime
from .models import Comment
from .forms import CommentForm


def update_comment(request):
    data = {}    
    referer = request.META.get('HTTP_REFERER', reverse('home'))
    #传入user来处理user验证问题
    comment_form = CommentForm(request.POST, user=request.user)
    if comment_form.is_valid():
        comment = Comment()
        comment.user = comment_form.cleaned_data['user']
        comment.text = comment_form.cleaned_data['text']
        comment.content_object = comment_form.cleaned_data['model_obj']

        parent = comment_form.cleaned_data['parent']
        if not parent is None:
            comment.root = parent.root if not parent.root is None else parent
            comment.parent = parent
            comment.reply_to = parent.user

        comment.save()
#        return redirect(referer)
#    else:
#        return render(request, 'error.html', {'message': comment_form.errors, 'redirect_to': referer})

        #返回json数据
        data['status'] = 'SUCCESS'
        data['username'] = comment.user.username
        #django的时间问题,需要转换成本地时间
        data['comment_time'] = localtime(comment.comment_time).strftime('%Y-%m-%d %H:%M:%S')
        data['text'] = comment.text

        if not parent is None:
            data['reply_to'] = comment.reply_to.username
        else:
            data['reply_to'] = ''

        data['pk'] = comment.pk
        data['root_pk'] = comment.root.pk if not comment.root is None  else ''

    else:
        data['status'] = 'ERROR'
        data['message'] = list(comment_form.errors.values())[0][0]
    return JsonResponse(data)