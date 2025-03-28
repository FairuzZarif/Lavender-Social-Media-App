from django.shortcuts import render, get_object_or_404
from .serializers import *
from inbox.models import *
from core.models import *
from .models import *
from authors.views import *
from posts.views import *
from inbox.views import *
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from core.schema_defs import *

local_host = settings.LOCAL_HOST
api_host = settings.API_HOST

class APIView(APIView):

    http_method_names = ['get', 'post', 'put', 'patch', 'delete']
    permission_classes = [AllowAny]

    def get(self, request):
        data = {
            "name": "Lavender Social Media API",
            "requestType": "GET",
        }
        return Response(status = status.HTTP_200_OK, data = data)

    def post(self, request):
        data = {
            "name": "Lavender Social Media API",
            "requestType": "POST",
        }
        return Response(status = status.HTTP_200_OK, data = data)

    def put(self, request):
        data = {
            "name": "Lavender Social Media API",
            "requestType": "PUT",
        }
        return Response(status = status.HTTP_200_OK, data = data)

    def patch(self, request):
        data = {
            "name": "Lavender Social Media API",
            "requestType": "PATCH",
        }
        return Response(status = status.HTTP_200_OK, data = data)

    def delete(self, request):
        data = {
            "name": "Lavender Social Media API",
            "requestType": "DELETE",
        }
        return Response(status = status.HTTP_200_OK, data = data)

def author_followers(request, author_id):
    return render(request, 'followers.html')

def author_following(request, author_id):
    return render(request, 'following.html')

def is_local(author_id):
    """
    Check if the author_id is local.
    @param author_id: Full URL ID for an author.
    """
    return author_id.startswith(api_host)

def is_remote_access(request):
    """
    Check if the request is a remote access, check core -> Authentication.py to understand the node setup
    """
    return request.user.username == "remoteauth"

def isFollowed(userid_a, userid_b):
    """
    Check if user_a is following user_b.
    @param user_a: Full URL ID for a user.
    @param user_b: Full URL ID for another user.
    """
    actor = get_object_or_404(AuthorModel, id = userid_a)
    object = get_object_or_404(AuthorModel, id = userid_b)
    return FollowerModel.objects.filter(actor = actor, object = object).exists()

def isFriend(userid_a, userid_b):
    """
    Check if user_a is friend with user_b.
    @param user_a: Full URL ID for a user.
    @param user_b: Full URL ID for another user.
    """
    actor = get_object_or_404(AuthorModel, id = userid_a)
    object = get_object_or_404(AuthorModel, id = userid_b)
    return (
        FollowerModel.objects.filter(actor = actor, object = object).exists()
        and FollowerModel.objects.filter(actor = object, object = actor).exists()
    )

class FollowingView(APIView):

    http_method_names = ['get']
    permission_classes = [IsAuthenticated]

    @SchemaDefinitions.following_view_get
    def get(self, request, actor_pk):
        """
        Get all following of actor_pk.
        """
        if is_remote_access(request):
            return Response(
                status = status.HTTP_403_FORBIDDEN,
                data = {"error": "Remote access is forbidden."}
            )
        actor_id = LinkGenerator("aa", [actor_pk]).generate()
        actor = get_object_or_404(AuthorModel, id = actor_id)
        following = FollowerModel.objects.filter(actor = actor)
        serializer = FollowerSerializer(following, many = True)
        for data in serializer.data:
            data["object"] = remove_kvpair(["username", "password", "lastGithubUpdate", "isVerified"], data["object"])
        data = {
            "type": "following",
            "following": serializer.data
        }
        return Response(status = status.HTTP_200_OK, data = data)

class FollowersView(APIView):

    http_method_names = ['get']
    permission_classes = [IsAuthenticated]

    @SchemaDefinitions.followers_view_get
    def get(self, request, object_pk):
        """
        Get all followers of object_pk.
        """
        object_id = LinkGenerator("aa", [object_pk]).generate()
        object = get_object_or_404(AuthorModel, id = object_id)
        followers = FollowerModel.objects.filter(object = object)
        serializer = FollowerSerializer(followers, many = True)
        response_data = []
        for data in serializer.data:
            author_data = remove_kvpair(
                ["username", "password", "lastGithubUpdate", "isVerified"],
                data["actor"]
            )
            response_data.append(author_data)
        data = {
            "type": "followers",
            "followers": response_data
        }
        return Response(status = status.HTTP_200_OK, data = data)

class FollowerRemoteView(APIView):

    http_method_names = ['get']
    permission_classes = [IsAuthenticated]

    @SchemaDefinitions.follower_remote_view_get
    def get(self, request, actor_pk, object_id):
        """
        Check if the actor_id is following the object_id, with identity verification.
        """
        if is_remote_access(request):
            return Response(
                status = status.HTTP_403_FORBIDDEN,
                data = {"error": "Remote access is forbidden."}
            )
        if actor_pk != request.user.username:
            return Response(status = status.HTTP_403_FORBIDDEN)
        actor_id = LinkGenerator("aa", [actor_pk]).generate()
        if not isFollowed(actor_id, object_id):
            return Response(status = status.HTTP_404_NOT_FOUND)
        return Response(status = status.HTTP_200_OK)

class FollowerView(APIView):

    http_method_names = ['get', 'put', 'delete']
    permission_classes = [IsAuthenticated]

    @SchemaDefinitions.follower_view_get
    def get(self, request, object_pk, actor_id):
        """
        Check if the actor_id is following the object_pk, with identity verification.
        """
        object_id = LinkGenerator("aa", [object_pk]).generate()
        if not isFollowed(actor_id, object_id):
            return Response(status = status.HTTP_404_NOT_FOUND)
        actor = get_object_or_404(AuthorModel, id = actor_id)
        data = remove_kvpair(
            ["username", "password", "lastGithubUpdate", "isVerified"],
            AuthorSerializer(actor).data
        )
        return Response(status = status.HTTP_200_OK, data = data)

    @SchemaDefinitions.follower_view_put
    def put(self, request, object_pk, actor_id):
        """
        Add a follower, with identity verification.
        """
        if is_remote_access(request):
            return Response(
                status = status.HTTP_403_FORBIDDEN,
                data = {"error": "Remote access is forbidden."}
            )
        if object_pk != request.user.username:
            return Response(status = status.HTTP_403_FORBIDDEN)
        object_id = LinkGenerator("aa", [object_pk]).generate()
        actor = get_object_or_404(AuthorModel, id = actor_id)
        object = get_object_or_404(AuthorModel, id = object_id)
        serializer = FollowerSerializer(data = {}, partial = True)
        if not serializer.is_valid():
            return Response(status = status.HTTP_400_BAD_REQUEST, data = serializer.errors)
        serializer.save(actor = actor, object = object)
        return Response(status = status.HTTP_201_CREATED)

    @SchemaDefinitions.follower_view_delete
    def delete(self, request, object_pk, actor_id):
        """
        Remove a follower, with identity verification.
        """
        if is_remote_access(request):
            return Response(
                status = status.HTTP_403_FORBIDDEN,
                data = {"error": "Remote access is forbidden."}
            )
        if object_pk != request.user.username:
            return Response(status = status.HTTP_403_FORBIDDEN)
        object_id = LinkGenerator("aa", [object_pk]).generate()
        actor = get_object_or_404(AuthorModel, id = actor_id)
        object = get_object_or_404(AuthorModel, id = object_id)
        follow_request = FollowRequestModel.objects.filter(object = object, actor = actor)
        if follow_request.exists():
            follow_request.delete()
        FollowerModel.objects.filter(actor = actor, object = object).delete()
        return Response(status = status.HTTP_204_NO_CONTENT)

class FollowRequestsObjectEnd(APIView):

    http_method_names = ['get']
    permission_classes = [IsAuthenticated]

    @SchemaDefinitions.follow_requests_object_end_get
    def get(self, request, object_pk):
        """
        Get all follow requests for the user.
        """
        if is_remote_access(request):
            return Response(
                status = status.HTTP_403_FORBIDDEN,
                data = {"error": "Remote access is forbidden."}
            )
        if object_pk != request.user.username:
            return Response(status = status.HTTP_403_FORBIDDEN)
        object_id = LinkGenerator("aa", [object_pk]).generate()
        object = get_object_or_404(AuthorModel, id = object_id)
        follow_request = FollowRequestModel.objects.filter(object = object)
        data_displayed = []
        if follow_request.exists():
            serializer = FollowRequestSerializer(follow_request, many = True)
            for data in serializer.data:
                actor = get_object_or_404(AuthorModel, id = data["actor"])
                data_displayed.append({"profileImage": getattr(actor, "profileImage", ""), "id": data["actor"]})
        response = {"data_displayed": data_displayed}
        return Response(status = status.HTTP_200_OK, data = response)

class FollowRequestObjectEnd(APIView):

    http_method_names = ['post', 'delete']
    permission_classes = [IsAuthenticated]

    @SchemaDefinitions.follow_request_object_end_post
    def post(self, request, object_pk, actor_id):
        """
        Implies the user accepts a follow request, thus deletes it from the database.
        """
        if is_remote_access(request):
            return Response(
                status = status.HTTP_403_FORBIDDEN,
                data = {"error": "Remote access is forbidden."}
            )
        if object_pk != request.user.username:
            return Response(status = status.HTTP_403_FORBIDDEN)
        object_id = LinkGenerator("aa", [object_pk]).generate()
        actor = get_object_or_404(AuthorModel, id = actor_id)
        object = get_object_or_404(AuthorModel, id = object_id)
        aofr = FollowRequestModel.objects.filter(actor = actor, object = object)
        if not aofr.exists():
            return Response(status = status.HTTP_404_NOT_FOUND)
        aofr.delete()
        
        serializer = FollowerSerializer(data = {}, partial = True)
        if not serializer.is_valid():
            return Response(status = status.HTTP_400_BAD_REQUEST, data = serializer.errors)
        serializer.save(actor = actor, object = object)
        return Response(status = status.HTTP_201_CREATED)
        
    @SchemaDefinitions.follow_request_object_end_delete
    def delete(self, request, object_pk, actor_id):
        """
        Delete a follow request for the user.
        """
        if is_remote_access(request):
            return Response(
                status = status.HTTP_403_FORBIDDEN,
                data = {"error": "Remote access is forbidden."}
            )
        if object_pk != request.user.username:
            return Response(status = status.HTTP_403_FORBIDDEN)
        object_id = LinkGenerator("aa", [object_pk]).generate()
        actor = get_object_or_404(AuthorModel, id = actor_id)
        object = get_object_or_404(AuthorModel, id = object_id)
        aofr = FollowRequestModel.objects.filter(actor = actor, object = object)
        aof = FollowerModel.objects.filter(actor = actor, object = object)
        if not aofr.exists():
            return Response(status = status.HTTP_404_NOT_FOUND)
        aofr.delete()
        aof.delete()
        return Response(status = status.HTTP_204_NO_CONTENT)

class FollowRequestActorEnd(APIView):

    http_method_names = ['post', 'delete']
    permission_classes = [IsAuthenticated]

    @SchemaDefinitions.follow_request_actor_end_post
    def post(self, request, actor_pk, object_id):
        """
        Send a follow request to the user.
        """
        if is_remote_access(request):
            return Response(
                status = status.HTTP_403_FORBIDDEN,
                data = {"error": "Remote access is forbidden."}
            )
        if actor_pk != request.user.username:
            return Response(status = status.HTTP_403_FORBIDDEN)
        actor_id = LinkGenerator("aa", [actor_pk]).generate()
        actor = get_object_or_404(AuthorModel, id = actor_id)
        if actor_id == object_id:
            return Response(
                status = status.HTTP_400_BAD_REQUEST,
                data = {"error": "Actor and object cannot be the same."}
            )
        if not is_local(object_id):
            data = {
                "username": str(uuid.uuid4()),
                "password": "!",
                "isVerified": True,
                "id": object_id,
                "host": object_id[:object_id.find("/api/authors/")] + "/api/",
                "displayName": object_id[object_id.find("/api/authors/") + 13:],
            }
            if not AuthorModel.objects.filter(id = object_id).exists():
                AuthorModel(**data).save()
            object = AuthorModel.objects.get(id = object_id)
            if not FollowerModel.objects.filter(actor = actor_id, object = object_id).exists():
                FollowerModel(actor = actor, object = object).save()
            data = {
                "type": "follow",
                "summary": f'User {actor_id} wants to follow user {object_id}.',
                "actor": remove_kvpair(
                    ["username", "password", "lastGithubUpdate", "isVerified"],
                    AuthorSerializer(actor).data
                ),
                "object": remove_kvpair(
                    ["username", "password", "lastGithubUpdate", "isVerified"],
                    AuthorSerializer(object).data
                )
            }
            Outbox(request, data).follow()
            return Response(status = status.HTTP_201_CREATED)
        object = get_object_or_404(AuthorModel, id = object_id)
        if (FollowerModel.objects.filter(actor = actor, object = object).exists()
            or FollowRequestModel.objects.filter(actor = actor, object = object).exists()):
            return Response(status = status.HTTP_409_CONFLICT)
        data = {
            "summary": f'User {actor.displayName} wants to follow user {object.displayName}.',
            "actor": actor_id,
            "object": object_id
        }
        serializer = FollowRequestSerializer(data = data, partial = True)
        if not serializer.is_valid():
            return Response(status = status.HTTP_400_BAD_REQUEST, data = serializer.errors)
        serializer.save()
        return Response(status = status.HTTP_201_CREATED)

    @SchemaDefinitions.follow_request_actor_end_delete
    def delete(self, request, actor_pk, object_id):
        """
        Delete a follow request for the user.
        """
        if is_remote_access(request):
            return Response(
                status = status.HTTP_403_FORBIDDEN,
                data = {"error": "Remote access is forbidden."}
            )
        if actor_pk != request.user.username:
            return Response(status = status.HTTP_403_FORBIDDEN)
        actor_id = LinkGenerator("aa", [actor_pk]).generate()
        actor = get_object_or_404(AuthorModel, id = actor_id)
        object = get_object_or_404(AuthorModel, id = object_id)
        aofr = FollowRequestModel.objects.filter(object = object, actor = actor)
        aof = FollowerModel.objects.filter(actor = actor, object = object)
        if aofr.exists():
            aofr.delete()
        if not aof.exists():
            return Response(status = status.HTTP_400_BAD_REQUEST)
        aof.delete()
        return Response(status = status.HTTP_204_NO_CONTENT)
    
class LinkGenerator:

    def __init__(self, mode, args):
        """
        Params: mode, args

        For the “mode” parameter, please select according to the format of the ID you need:
        "a"    - http://node/(a)uthors/1
        "ap"   - http://node/(a)uthors/1/(p)osts/2
        "apc"  - http://node/(a)uthors/1/(p)osts/2/(c)omments
        "acl"  - http://node/(a)uthors/1/(c)omments/2/(l)ikes
        "aa"   - http://node/(a)pi/(a)uthors/1
        "aal"  - http://node/(a)pi/(a)uthors/1/(l)iked/2
        "aap"  - http://node/(a)pi/(a)uthors/1/(p)osts/2
        "aapc" - http://node/(a)pi/(a)uthors/1/(p)osts/2/(c)omments
        "aapl" - http://node/(a)pi/(a)uthors/1/(p)osts/2/(l)ikes
        "aac"  - http://node/(a)pi/(a)uthors/1/(c)ommented/2
        "aacl" - http://node/(a)pi/(a)uthors/1/(c)ommented/2/(l)ikes
        """
        self.dict = {
            "a": [1, "authors/"],
            "ap": [2, "authors/", "/posts/"],
            "apc": [2, "authors/", "/posts/", "/comments"],
            "acl": [2, "authors/", "/comments/", "/likes"],
            "aa": [1, "api/authors/"],
            "aal": [2, "api/authors/", "/liked/"],
            "aap": [2, "api/authors/", "/posts/"],
            "aapc": [2, "api/authors/", "/posts/", "/comments"],
            "aapl": [2, "api/authors/", "/posts/", "/likes"],
            "aac": [2, "api/authors/", "/commented/"],
            "aacl": [2, "api/authors/", "/commented/", "/likes"]
        }
        self.mode = mode
        self.args = args
        self.returnee = ""

    def is_args_legal(self):
        if len(self.args) != self.dict[self.mode][0]:
            return False
        return True

    def add_absolute_uri(self):
        self.args.insert(0, local_host)

    def merge(self):
        args_len = len(self.args)
        modelst = self.dict[self.mode]
        modelst.pop(0)
        modelst_len = len(modelst)
        counter = 0
        while counter < args_len or counter < modelst_len:
            if counter < args_len:
                self.returnee += str(self.args[counter])
            if counter < modelst_len:
                self.returnee += str(modelst[counter])
            counter += 1

    def generate(self):
        if not self.is_args_legal():
            return -1
        self.add_absolute_uri()
        self.merge()
        return self.returnee
    
def remove_kvpair(keys, data):
    """
    Remove key-value pairs from a dictionary or a list of dictionaries.
    """
    if len(keys) == 0:
        return data
    if isinstance(data, ReturnList) or isinstance(data, list):
        if len(data) == 0:
            return data
        for i in range(len(data)):
            for key in keys:
                data[i].pop(key)
    elif isinstance(data, ReturnDict) or isinstance(data, dict):
        for key in keys:
            data.pop(key)
    return data
