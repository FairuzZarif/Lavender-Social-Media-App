from django.shortcuts import render
from authors.views import *
from follow.views import *
from core.views import *
from authors.models import *
from follow.models import *
from core.models import *
from .models import *
import base64
import json
import os
import re
import uuid
import requests
import threading

class InboxView(APIView):

    http_method_names = ['post']
    permission_classes = [IsAuthenticated]

    @SchemaDefinitions.inbox_view_post
    def post(self, request, author_pk):
        """
        Receive a message from another author.
        """
        if not request.data or "type" not in request.data:
            return Response(
                status = status.HTTP_400_BAD_REQUEST,
                data = {"detail": "Illegal request."}
            )
        if request.data["type"] == "post":
            regex = r'^(http|https)://[^\/]+/?[^\/]*/api/authors/[^\/]+/posts/[^\/]+$'
            if not re.fullmatch(regex, request.data["id"]):
                return Response(
                    status = status.HTTP_400_BAD_REQUEST,
                    data = {"detail": "Illegal Post ID."}
                )
        return Response(status = Inbox(request, author_pk).run())

class Inbox:

    def __init__(self, request, author_pk):
        self.dict = {
            "follow": self.handle_follow,
            "post": self.handle_post,
            "comment": self.handle_comment,
            "like": self.handle_like
        }
        self.request = request
        self.data = self.request.data
        self.type = self.data["type"]
        self.author_pk = author_pk
    
    def run(self):
        self.update_follower()
        if self.type not in self.dict:
            return status.HTTP_400_BAD_REQUEST
        return self.dict[self.type]()
    
    def get_credential(self, node):
        ori = node.outUsername + ":" + node.outPassword
        return base64.b64encode(ori.encode()).decode()
    
    def update_follower(self):
        followers = FollowerModel.objects.all()
        nodes = ShareNodeModel.objects.all()
        if not followers or not nodes:
            return
        checklst = []
        for follower in followers:
            for node in nodes:
                if node.host in follower.object.host:
                    checklst.append(follower)
                    break
        for follower in checklst:
            url = f"{follower.object.id}/followers/{follower.actor.id}"
            headers = {
                "X-Original-Host": api_host,
                "Authorization": f"Basic {self.get_credential(node)}",
            }
            try:
                response = requests.get(url, headers = headers)
            except:
                continue
            if response.status_code == 404:
                follower.delete()

    def handle_follow(self):
        mustlst = ["type", "summary", "actor", "object"]
        for must in mustlst:
            if not self.data.get(must):
                return status.HTTP_400_BAD_REQUEST
        mustlstsl = ["type", "id"]
        for must in mustlstsl:
            if not self.data["actor"].get(must) or not self.data["object"].get(must):
                return status.HTTP_400_BAD_REQUEST
        actor = get_or_make_author(self.data["actor"])
        if not actor:
            return status.HTTP_400_BAD_REQUEST
        object = get_object_or_404(AuthorModel, id = self.data["object"]["id"])
        if (FollowerModel.objects.filter(actor = actor, object = object).exists()
            or FollowRequestModel.objects.filter(actor = actor, object = object).exists()):
            return status.HTTP_200_OK
        FollowerModel(actor = actor, object = object).save()
        data = {
            "summary": self.data["summary"],
            "actor": actor.id,
            "object": object.id
        }
        serializer = FollowRequestSerializer(data = data, partial = True)
        if not serializer.is_valid():
            return status.HTTP_400_BAD_REQUEST
        serializer.save()
        return status.HTTP_200_OK

    def handle_post(self):
        mustlst = ["type", "id", "author", "title", "contentType", "content", "published", "visibility"]
        for must in mustlst:
            if not self.data.get(must):
                return status.HTTP_400_BAD_REQUEST
        mustlstsl = ["type", "id"]
        for must in mustlstsl:
            if not self.data["author"].get(must):
                return status.HTTP_400_BAD_REQUEST
        if not get_or_make_post(self.data):
            return status.HTTP_400_BAD_REQUEST
        return status.HTTP_200_OK

    def handle_comment(self):
        mustlst = ["type", "id", "author", "post", "contentType", "comment", "published"]
        for must in mustlst:
            if not self.data.get(must):
                return status.HTTP_400_BAD_REQUEST
        mustlstsl = ["type", "id"]
        for must in mustlstsl:
            if not self.data["author"].get(must):
                return status.HTTP_400_BAD_REQUEST
        post = PostModel.objects.filter(id = self.data.get("post")).first()
        if not post:
            return status.HTTP_200_OK
        data = {
            "id": self.data["id"],
            "post": self.data["post"],
            "contentType": self.data["contentType"],
            "comment": self.data["comment"],
            "published": self.data["published"]
        }
        serializer = CommentSerializer(data = data, partial = True)
        if not serializer.is_valid():
            return status.HTTP_400_BAD_REQUEST
        author = get_or_make_author(self.data["author"])
        if not author:
            return status.HTTP_400_BAD_REQUEST
        serializer.save(author = author)
        return status.HTTP_200_OK

    def handle_like(self):
        mustlst = ["type", "id", "author", "object", "published"]
        for must in mustlst:
            if not self.data.get(must):
                return status.HTTP_400_BAD_REQUEST
        mustlstsl = ["type", "id"]
        for must in mustlstsl:
            if not self.data["author"].get(must):
                return status.HTTP_400_BAD_REQUEST
        if ("posts" not in self.data.get("object")
            and "commented" not in self.data.get("object")):
            return status.HTTP_400_BAD_REQUEST
        is_post = "posts" in self.data.get("object")
        object = (
            PostModel.objects.filter(id = self.data.get("object")).first() if is_post
            else CommentModel.objects.filter(id = self.data.get("object")).first()
        )
        if not object:
            return status.HTTP_200_OK
        data = {
            "id": self.data["id"],
            "published": self.data["published"],
            "object": self.data["object"]
        }
        serializer = LikeSerializer(data = data, partial = True)
        if not serializer.is_valid():
            return status.HTTP_400_BAD_REQUEST
        author = get_or_make_author(self.data["author"])
        if not author:
            return status.HTTP_400_BAD_REQUEST
        serializer.save(author = author, post = object) if is_post else serializer.save(author = author, comment = object)
        return status.HTTP_200_OK

class Outbox:

    def __init__(self, request, data):
        self.request = request
        self.data = data
        self.shared_nodes = ShareNodeModel.objects.all()
    
    def follow(self):
        node = None
        for shared_node in self.shared_nodes:
            if self.data["object"]["id"].startswith(shared_node.host):
                node = shared_node
        if node == None:
            return
        self.departure(node.host, self.data["object"]["id"].split("/")[-1], node)

    def send(self):
        for node in self.shared_nodes:
            lfs = None
            author = get_object_or_404(AuthorModel, id = self.data["author"]["id"])
            for follower in FollowerModel.objects.filter(object = author):
                if follower.actor.host == node.host:
                    lfs = follower.actor.id.split("/")[-1]
            if lfs == None:
                continue
            self.departure(node.host, lfs, node)

    def get_credential(self, node):
        ori = node.outUsername + ":" + node.outPassword
        return base64.b64encode(ori.encode()).decode()

    def departure(self, host, author_serial, node):
        if not node.allowOut:
            return
        url = f"{host}authors/{author_serial}/inbox"
        headers = {
            "X-Original-Host": str(self.request.build_absolute_uri("/")) + "api/",
            "Authorization": f"Basic {self.get_credential(node)}",
            "Content-Type": "application/json"
        }
        thread = threading.Thread(
            target = self.takeoff,
            args = (url, headers, json.dumps(self.data))
        )
        thread.start()
    
    def takeoff(self, url, headers, data):
        try:
            requests.post(url, headers = headers, data = data)
        except:
            return
        
def get_or_make_author(author_data):
    mstlst = ["type", "id", "host", "page"]
    for mst in mstlst:
        if not author_data.get(mst):
            return None
    author = AuthorModel.objects.filter(id = author_data["id"]).first()
    if author:
        fields = ["type", "host", "displayName", "github", "profileImage", "page"]
        updated = False
        for field in fields:
            if not author_data.get(field):
                continue
            if getattr(author, field) != author_data[field]:
                setattr(author, field, author_data[field])
                updated = True
        if updated:
            author.save()
        return author
    data = {
        "username": str(uuid.uuid4()),
        "password": "!",
        "type": "author",
        "id": author_data["id"],
        "host": author_data["host"],
        "displayName": author_data["id"][author_data["id"].find("/api/authors/") + 13:],
        "page": author_data["page"],
        "isVerified": True,
    }
    optlst = ["displayName", "github", "profileImage"]
    for opt in optlst:
        if author_data.get(opt):
            data[opt] = author_data[opt]
    serializer = AuthorSerializer(data = data, partial=True)
    if not serializer.is_valid():
        return None
    author = serializer.save()
    return author

def get_or_make_post(request_data):
    mustlst = ["type", "id", "author", "title", "contentType", "content", "published", "visibility"]
    for must in mustlst:
        if not request_data.get(must):
            return None
    author = get_or_make_author(request_data["author"])
    if not author:
        return None
    contentType = ["text/plain", "text/markdown", "application/base64", "image/png;base64", "image/jpeg;base64"]
    if (not request_data.get("contentType")
        or request_data["contentType"] not in contentType):
        return None
    post = PostModel.objects.filter(id = request_data["id"]).first()
    if post:
        fields = ["type", "title", "description", "contentType", "content", "visibility"]
        updated = False
        for field in fields:
            if not request_data.get(field):
                continue
            if getattr(post, field) != request_data[field]:
                setattr(post, field, request_data[field])
                updated = True
        if updated:
            post.save()
        return post
    data = {
        "type": request_data["type"],
        "id": request_data["id"],
        "title": request_data["title"],
        "contentType": request_data["contentType"],
        "content": request_data["content"],
        "published": request_data["published"],
        "visibility": request_data["visibility"]
    }
    optlst = ["description"]
    for opt in optlst:
        if request_data.get(opt):
            data[opt] = request_data[opt]
    serializer = PostSerializer(data = data, partial = True)
    if not serializer.is_valid():
        return None
    post = serializer.save(author = author)
    return post
