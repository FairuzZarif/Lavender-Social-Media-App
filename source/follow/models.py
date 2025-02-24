from django.db import models
from authors.models import AuthorModel

class FollowerModel(models.Model):
    mid = models.AutoField(primary_key = True)
    actor = models.ForeignKey(AuthorModel, to_field = "id", on_delete = models.CASCADE, related_name = "follower")
    object = models.ForeignKey(AuthorModel, to_field = "id", on_delete = models.CASCADE, related_name = "followee")


class FollowRequestModel(models.Model):
    mid = models.AutoField(primary_key = True)
    type = models.CharField(max_length = 64, default = "follow")
    summary = models.CharField(max_length = 512)
    actor = models.ForeignKey(AuthorModel, to_field = "id", on_delete = models.CASCADE, related_name = "actor")
    object = models.ForeignKey(AuthorModel, to_field = "id", on_delete = models.CASCADE, related_name = "object")
