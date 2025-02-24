from django.shortcuts import render, get_object_or_404 # type: ignore
from posts.views import handle_post_data
from rest_framework.views import APIView # type: ignore
from rest_framework.permissions import AllowAny, IsAuthenticated # type: ignore
from django.shortcuts import render, get_object_or_404 # type: ignore
from posts.views import handle_post_data
from rest_framework.views import APIView # type: ignore
from rest_framework.permissions import AllowAny, IsAuthenticated # type: ignore
from rest_framework import status # type: ignore
from rest_framework.response import Response #type: ignore
from socialapp import settings
from posts.serializers import PostSerializer # type: ignore

from .models import *
from posts.models import PostModel
from follow.models import FollowerModel, FollowRequestModel
from authors.views import *
from posts.views import *
from posts.serializers import *
from .serializers import *

from django.core.files.storage import default_storage #type: ignore
from django.core.files.base import ContentFile # type: ignore
from rest_framework.utils.serializer_helpers import ReturnDict, ReturnList #type: ignore
import uuid, os, requests #type: ignore

from core.schema_defs import *

local_host = settings.LOCAL_HOST
api_host = settings.API_HOST

class CommentsView(APIView):

    http_method_names = ['get']
    permission_classes = [IsAuthenticated]
    
    @SchemaDefinitions.comments_view_get
    def get(self, request, **kwargs):
        """
        Get all comments by post_id or author_pk and post_pk.
        """
        data = APCLJsonGenerator(request, **kwargs, mode = "comments").get_comments()
        return Response(status = status.HTTP_200_OK, data = data)


class CommentedView(APIView):

    http_method_names = ['get', 'post']
    permission_classes = [IsAuthenticated]

    @SchemaDefinitions.commented_view_get
    def get(self, request, **kwargs):
        """
        Get all commented posts by comment_id.
        """
        data = APCLJsonGenerator(request, **kwargs, mode = "commented").get_commented()
        return Response(status = status.HTTP_200_OK, data = data)

    @SchemaDefinitions.commented_view_post
    def post(self, request, **kwargs):
        """
        Create a new comment by author_pk.
        """
        if is_remote_access(request):
            return Response(
                status = status.HTTP_403_FORBIDDEN,
                data = {"error": "Remote access is forbidden."}
            )
        author_pk = kwargs.get("author_pk", None)
        post_id = request.data.get("post")
        author_id = LinkGenerator("aa", [author_pk]).generate()
        author = get_object_or_404(AuthorModel, id = author_id)
        post = get_object_or_404(PostModel, id = post_id)
        serializer = CommentSerializer(data=request.data, partial = True)
        if not serializer.is_valid():
            return Response(status = status.HTTP_400_BAD_REQUEST, data = serializer.errors)
        comment = serializer.save(author = author, post = post)
        comment.id = LinkGenerator("aac", [author_pk, comment.mid]).generate()
        comment.save()
        serializer = CommentSerializer(comment)
        data = remove_kvpair(["mid"], serializer.data)
        data["post"] = post.id
        temp = remove_kvpair(["username", "password", "lastGithubUpdate", "isVerified"], data["author"])
        data["author"] = temp
        Outbox(request, data).send()
        return Response(status=status.HTTP_201_CREATED, data = data)


class CommentView(APIView):

    http_method_names = ['get']
    permission_classes = [IsAuthenticated]
    
    @SchemaDefinitions.comment_view_get
    def get(self, request, **kwargs):
        """
        Get a comment by comment_id.
        """
        data = APCLJsonGenerator(request, **kwargs, mode = "comment").get_comment()
        return Response(status = status.HTTP_200_OK, data = data)


class LikesView(APIView):

    http_method_names = ['get']
    permission_classes = [IsAuthenticated]

    @SchemaDefinitions.likes_view_get
    def get(self, request, **kwargs):
        """
        Get all likes by author_pk and post_pk or author_id.
        """
        author_pk = kwargs.get("author_pk", None)
        post_pk = kwargs.get("post_pk", None)
        post_id = kwargs.get("post_id", None)
        comment_id = kwargs.get("comment_id", None)
        author_id = kwargs.get("author_id", None)
        if ((author_pk != None) and (post_pk != None) and (comment_id == None)):
            data = APCLJsonGenerator(request, **kwargs, mode = "likes").get_post_likes()
            return Response(status = status.HTTP_200_OK, data = data)
        if (post_id != None):
            data = APCLJsonGenerator(request, **kwargs, mode = "likes").get_post_likes()
            return Response(status = status.HTTP_200_OK, data = data)
        if ((author_pk != None) and (post_pk != None) and (comment_id != None)):
            data = APCLJsonGenerator(request, **kwargs, mode = "likes").get_comment_likes()
            return Response(status = status.HTTP_200_OK, data = data)
        if ((author_pk != None) and (post_pk == None) and (comment_id == None)):
            data = APCLJsonGenerator(request, **kwargs, mode = "liked").get_liked()
            return Response(status = status.HTTP_200_OK, data = data)
        if (author_id != None):
            data = APCLJsonGenerator(request, **kwargs, mode = "liked").get_liked()
            return Response(status = status.HTTP_200_OK, data = data)


class LikeView(APIView):

    http_method_names = ['get', 'post']
    permission_classes = [IsAuthenticated]

    @SchemaDefinitions.like_view_get
    def get(self, request, **kwargs):
        """
        Get a like by like_id.
        """
        data = APCLJsonGenerator(request, **kwargs, mode = "like").get_like()
        return Response(status = status.HTTP_200_OK, data = data)

    @SchemaDefinitions.like_view_post
    def post(self, request, **kwargs):
        """
        Create a new like by author_pk.
        """
        if is_remote_access(request):
            return Response(
                status = status.HTTP_403_FORBIDDEN,
                data = {"error": "Remote access is forbidden."}
            )
        author_pk = kwargs.get("author_pk", None)
        author_id = LinkGenerator("aa", [author_pk]).generate()
        author = get_object_or_404(AuthorModel, id = author_id)
        if "post" in request.data:
            post = get_object_or_404(PostModel, id = request.data["post"])
            if post.visibility == 'DELETED':
                return Response(status = status.HTTP_404_NOT_FOUND)
            author_likes_exist = LikeModel.objects.filter(author = author_id, object = request.data["post"]).exists()
            if author_likes_exist:
                return Response(status = status.HTTP_409_CONFLICT)
        elif "comment" in request.data:
            get_object_or_404(CommentModel, id = request.data["comment"])
            author_likes_exist = LikeModel.objects.filter(author = author_id, object = request.data["comment"]).exists()
            if author_likes_exist:
                return Response(status = status.HTTP_409_CONFLICT)

        serializer = LikeSerializer(data = request.data, partial = True)
        if not (serializer.is_valid()):
            return Response(status = status.HTTP_400_BAD_REQUEST, data = serializer.errors)
        like = serializer.save(author = author)
        like.id = LinkGenerator("aal", [author_pk, like.mid]).generate()
        if "post" in request.data:
            like.object = request.data["post"]
        elif "comment" in request.data:
            like.object = request.data["comment"]
        like.save()
        serializer = LikeSerializer(like)
        data = remove_kvpair(["post", "comment", "mid"], serializer.data)
        temp = remove_kvpair(["username", "password", "lastGithubUpdate", "isVerified"], data["author"])
        data["author"] = temp
        Outbox(request, data).send()
        return Response(status = status.HTTP_201_CREATED, data = data)