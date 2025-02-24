from django.db import models

class CommentModel(models.Model):
    from authors.models import AuthorModel
    
    mid = models.AutoField(primary_key = True)
    type = models.CharField(max_length = 64, default = "comment")
    id = models.CharField(unique = True, max_length = 1024)
    author = models.ForeignKey(AuthorModel, to_field = "id", on_delete = models.CASCADE, related_name = "comment_author")
    post = models.ForeignKey('posts.PostModel', to_field = "id", on_delete = models.CASCADE, related_name = "comment_post")
    contentType = models.CharField(max_length = 64, choices = [("text/plain", "Plain Text"),("text/markdown", "Markdown")])
    comment = models.TextField()
    published = models.DateTimeField(auto_now_add = True)


class LikeModel(models.Model):
    from authors.models import AuthorModel
    
    mid = models.AutoField(primary_key = True)
    post = models.ForeignKey('posts.PostModel', to_field = "id", on_delete = models.CASCADE, related_name = "like_post", null = True, blank = True)
    comment = models.ForeignKey(CommentModel, to_field = "id", on_delete = models.CASCADE, related_name = "like_comment", null = True, blank = True)
    type = models.CharField(max_length = 64, default = "like")
    id = models.CharField(unique = True, max_length = 1024)
    author = models.ForeignKey(AuthorModel, to_field = "id", on_delete = models.CASCADE, related_name = "like_author")
    object = models.CharField(max_length = 1024)
    published = models.DateTimeField(auto_now_add = True)
