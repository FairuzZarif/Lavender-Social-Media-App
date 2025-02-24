from rest_framework import serializers
from .models import *

class AuthorSerializer(serializers.ModelSerializer):

    class Meta:
        model = AuthorModel
        fields = "__all__"