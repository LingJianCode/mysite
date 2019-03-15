from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from ckeditor.widgets import CKEditorWidget
from .models import Comment

class CommentForm(forms.Form):
    content_type = forms.CharField(widget=forms.HiddenInput)
    object_id = forms.IntegerField(widget=forms.HiddenInput)
    #lable=False 去掉前端显示的label
    text = forms.CharField(widget=CKEditorWidget(config_name='comment_ckeditor'), label=False, error_messages={'required':'评论内容不能为空'})

    reply_comment_id = forms.IntegerField(widget=forms.HiddenInput(attrs={'id':'reply_comment_id'}))

    def __init__(self, *args, **kwargs):
        if 'user' in kwargs:
            #必须将自定义的的参数拿出，不然报错??
            self.user = kwargs.pop('user')
        super(CommentForm, self).__init__(*args, **kwargs)

    def clean(self):
        #判断用户是否登录
        if self.user.is_authenticated:
            self.cleaned_data['user'] = self.user
        else:
            raise forms.ValidationError('用户尚未登录')


        #评论对下验证
        content_type = self.cleaned_data['content_type']
        object_id = self.cleaned_data['object_id']
        try:
            #获取到对应的对象
            model_class = ContentType.objects.get(model=content_type).model_class()
            model_obj = model_class.objects.get(pk=object_id)
            #为了views保存评论而返回
            self.cleaned_data['model_obj'] = model_obj
        except ObjectDoesNotExist:
            raise forms.ValidationError('评论对象不存在')

        return self.cleaned_data

    def clean_reply_comment_id(self):
        reply_comment_id = self.cleaned_data['reply_comment_id']
        if reply_comment_id < 0 :
            raise forms.ValidationError('回复错误')
        #为0则是根回复
        elif reply_comment_id == 0:
            self.cleaned_data['parent'] = None
        #不为0则是回复别人，需要判断是否在数据库中存在
        elif Comment.objects.filter(pk=reply_comment_id).exists():
            self.cleaned_data['parent'] = Comment.objects.get(pk=reply_comment_id)
        else:
            raise forms.ValidationError('回复错误')

        return reply_comment_id