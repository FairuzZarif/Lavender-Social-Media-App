from django.db import models

class PostModel(models.Model):
    from authors.models import AuthorModel
    from comments_likes.models import CommentModel, LikeModel
    
    availble_types = [
        ("text/plain", "Plain Text"),
        ("text/markdown", "Markdown"),
        ("application/base64", "Image"),
        ("image/png;base64", "PNG"),
        ("image/jpeg;base64", "JPEG"),
    ]
    availble_visibility = [
        ("PUBLIC", "Public"),
        ("FRIENDS", "Friends"),
        ("UNLISTED", "Unlisted"),
        ("DELETED", "Deleted"),
    ]
    mid = models.AutoField(primary_key = True)
    type = models.CharField(max_length = 64, default = "post")
    id = models.CharField(unique = True, max_length = 1024)
    author = models.ForeignKey(AuthorModel, to_field='id', on_delete = models.CASCADE)
    title = models.TextField()
    description = models.TextField()
    contentType = models.CharField(max_length = 64, choices = availble_types)
    content = models.TextField()
    published = models.DateTimeField(auto_now_add = True)
    visibility = models.CharField(max_length = 64, choices = availble_visibility)