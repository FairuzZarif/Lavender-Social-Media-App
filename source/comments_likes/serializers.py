from rest_framework import serializers
from .models import *
from authors.serializers import *

class CommentSerializer(serializers.ModelSerializer):
    author = AuthorSerializer()

    class Meta:
        model = CommentModel
        fields = "__all__"


class LikeSerializer(serializers.ModelSerializer):
    author = AuthorSerializer()

    class Meta:
        model = LikeModel
        fields = "__all__"
