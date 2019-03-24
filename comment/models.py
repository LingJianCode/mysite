from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User

#models.CASCADE 级联删除，删除这个，会将它关联的数据给删除
class Comment(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    text = models.TextField()
    comment_time = models.DateTimeField(auto_now_add=True)
    #related_name由于有两个字段外键了User所以必须指定相应的关系
    user = models.ForeignKey(User, related_name="comments",on_delete=models.CASCADE)

    #树型结构
    #顶级评论
    root = models.ForeignKey('self', related_name="root_comment",null=True, on_delete=models.CASCADE)
    #父评论
    parent = models.ForeignKey('self', related_name="parent_comment", null=True, on_delete=models.CASCADE)
    #回复谁
    reply_to = models.ForeignKey(User, related_name="replies" ,null=True, on_delete=models.CASCADE)

    def  __str__(self):
        return str(self.object_id)+'||'+self.text[0:50]

    class Meta:
        ordering = ['comment_time']