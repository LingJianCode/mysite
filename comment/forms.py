from django import forms

class CommentForm(forms.Form):
    content_type = forms.CharField()
    object_id = forms.IntergerField()
    text = forms.CharField()