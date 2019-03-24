from django import template
from django.contrib.contenttypes.models import ContentType
from ..models import Comment


#自定义模板标签
#可以降低代码耦合度，减少views代码量

register = template.Library()


@register.simple_tag
def test(a):
    return '测试自定义标签: ' + a



#获取评论数，通过自定义标签来实现在blog_list时展示评论数
#其他阅读数、表单都可以这样处理
@register.simple_tag
def get_comment_count(obj):
    content_type = ContentType.objects.get_for_model(obj)
    return Comment.objects.filter(content_type=content_type, object_id=obj.pk).count()