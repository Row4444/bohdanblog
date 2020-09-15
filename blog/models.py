from django.conf import settings
from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField


# Create your models here.


class Article(models.Model):
    STATUS_CHOICES = (
        ('u', 'Unview'),
        ('a', 'Approve'),
        ('d', 'Decline')
    )
    title = models.CharField(max_length=120, unique=True)
    body = RichTextUploadingField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    background_img = models.ImageField(upload_to='backgrounds/%Y/%m/%d', null=True, blank=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='u')

    def __str__(self):
        return self.title


class Like(models.Model):
    like_dislike = [
        (True, 'Like'),
        (False, 'Dislike')
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    like = models.BooleanField(choices=like_dislike)


class Comment(models.Model):
    post = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    body = models.CharField(max_length=140)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('date',)

    def __str__(self):
        return '{}'.format(self.body)
