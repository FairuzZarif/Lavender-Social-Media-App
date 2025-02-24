from rest_framework import serializers
from .models import *
from authors.serializers import AuthorSerializer

class FollowerSerializer(serializers.ModelSerializer):
    actor = AuthorSerializer()
    object = AuthorSerializer()

    class Meta:
        model = FollowerModel
        fields = ['actor', 'object']
        
class FollowRequestSerializer(serializers.ModelSerializer):
    actor = AuthorModel()
    object = AuthorModel()
    
    class Meta:
        model = FollowRequestModel
        fields = "__all__"