from django.conf import settings # type: ignore
from django.http import FileResponse
from PIL import Image # type: ignore
from .models import *
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.utils.serializer_helpers import ReturnDict, ReturnList #type: ignore
from comments_likes.serializers import CommentSerializer, LikeSerializer
from .serializers import PostSerializer
from comments_likes.models import LikeModel, CommentModel
from authors.views import *
from follow.views import *
from inbox.views import *
import base64
import json
import os
import re
import uuid
import requests # type: ignore
import threading
from core.schema_defs import *
from django.db.models import Q

fp_post_image = os.path.relpath(os.path.join(settings.IMAGE_ROOT, f'imagePost_images/'))

def handle_post_data(author_id, data):
    if data["contentType"] not in ["text/plain", "text/markdown"]:
        if not validate_image_file(data["content"], data["contentType"], mode = "in"):
            image_path = os.path.join(settings.BASE_DIR, "static", "img", "invalidImage.png")
            with open(image_path, 'rb') as image_file:
                default = image_file.read()
            data["content"] = "data:image/jpeg;base64," + base64.b64encode(default).decode("utf-8")
    data = remove_kvpair(["mid"], data)
    temp = remove_kvpair(["username", "password", "isVerified", "lastGithubUpdate"], data["author"])
    data["author"] = temp
    likes = LikeModel.objects.filter(object = data["id"]).order_by('-published')
    data["isLiked"] = False
    for like in likes:
        if like.author.id == author_id:
            data["isLiked"] = True
            break
        
def validate_image_file(post_content, content_type, mode):
    data = post_content.split(";base64,")[1]
    try:
        image_data = base64.b64decode(data)
    except:
        return None
    if content_type == "image/png;base64":
        name = standardize_post_image_name("png")
    elif content_type == "image/jpeg;base64":
        name = standardize_post_image_name("jpeg")
    elif content_type == "application/base64":
        image_type = post_content.split("/")[1].split(";")[0]
        if image_type == "svg+xml":
            image_type = "svg"
        name = standardize_post_image_name(image_type)
    else:
        return None
    os.makedirs(fp_post_image, exist_ok=True)
    with open(name, "wb") as image_file:
        image_file.write(image_data)
    try:
        img = Image.open(name)
        img.verify()
    except Exception:
        os.remove(name)
        return None
    else:
        if mode == "in":
            os.remove(name)
            return True
        else:
            return name
        
def standardize_post_image_name(image_type):
    """
    Standardize the post image name.
    """
    return fp_post_image + f"/{uuid.uuid4()}.{image_type}"

class PostsView(APIView):

    http_method_names = ['get', 'post']
    permission_classes = [IsAuthenticated]
    @SchemaDefinitions.posts_view_get
    def get(self, request, author_pk):
        """
        Get all posts by author_pk.
        """
        if is_remote_access(request):
            return Response(
                status = status.HTTP_403_FORBIDDEN,
                data = {"error": "Remote access is forbidden."}
            )
        user_pk = request.user.username
        user_id = LinkGenerator("aa", [user_pk]).generate()
        author_id = LinkGenerator("aa", [author_pk]).generate()
        author = get_object_or_404(AuthorModel, id = author_id)

        if user_pk == author_pk:
            posts = PostModel.objects.filter(
                Q(author = author) & ~(Q(visibility = "DELETED"))
            ).order_by('-published')
        elif isFriend(user_id, author_id):
            posts = PostModel.objects.filter(
                Q(author = author) & (Q(visibility = "PUBLIC") | Q(visibility = "FRIENDS") | Q(visibility = "UNLISTED"))
            ).order_by('-published')
        elif isFollowed(user_id, author_id):
            posts = PostModel.objects.filter(
                Q(author = author) & (Q(visibility = "PUBLIC") | Q(visibility = "UNLISTED"))
            ).order_by('-published')
        else:
            posts = PostModel.objects.filter(author = author, visibility = "PUBLIC").order_by('-published')
        
        serializer = PostSerializer(posts, many = True)
        for data in serializer.data:
            data = remove_kvpair(["mid", "content"], data)
            data["author"] = remove_kvpair(["username", "password", "lastGithubUpdate", "isVerified"], data["author"])
        return Response(status = status.HTTP_200_OK, data = serializer.data)

    @SchemaDefinitions.posts_view_post
    def post(self, request, author_pk):
        """
        Create a new post by author_pk.
        """
        if is_remote_access(request):
            return Response(
                status = status.HTTP_403_FORBIDDEN,
                data = {"error": "Remote access is forbidden."}
            )
        author_id = LinkGenerator("aa", [author_pk]).generate()
        author = get_object_or_404(AuthorModel, id = author_id)
        if request.data["contentType"] not in ["text/plain", "text/markdown"]:
            if not validate_image_file(request.data["content"], request.data["contentType"], mode = "in"):
                return Response(status = status.HTTP_400_BAD_REQUEST, data = {"error": "Unsupported Image Format."})
        serializer = PostSerializer(data = request.data, partial = True)
        if not serializer.is_valid():
            return Response(status = status.HTTP_400_BAD_REQUEST, data = serializer.errors)
        post = serializer.save(author = author)
        post.id = LinkGenerator("aap", [author_pk, post.mid]).generate()
        post.save()
        data = APCLJsonGenerator(request, post_id = post.id, mode = "post").get_post()
        Outbox(request, data).send()
        return Response(status = status.HTTP_201_CREATED, data = data)

class PostView(APIView):
    http_method_names = ['get', 'put', 'delete']
    permission_classes = [IsAuthenticated]

    @SchemaDefinitions.post_view_get
    def get(self, request, **kwargs):
        """
        Get a post by post_id or author_pk and post_pk.
        """
        user_id = LinkGenerator("aa", [request.user.username]).generate()
        author_pk = kwargs.get("author_pk", None)
        post_pk = kwargs.get("post_pk", None)
        post_id = kwargs.get("post_id", None)
        if author_pk and post_pk:
            post_id = LinkGenerator("aap", [author_pk, post_pk]).generate()
        post = get_object_or_404(PostModel, id = post_id)
        if is_remote_access(request) and post.visibility != "PUBLIC":
            return Response(
                status = status.HTTP_403_FORBIDDEN,
                data = {"error": "Remote access is forbidden."}
            )
        if post.visibility == "DELETED":
            return Response(status = status.HTTP_404_NOT_FOUND)
        if post.author.id != user_id:
            if (post.visibility == "FRIENDS"
                and not isFriend(user_id, post.author.id)):
                return Response(status = status.HTTP_404_NOT_FOUND)
        data = APCLJsonGenerator(request, **kwargs, mode = "post").get_post()
        return Response(status = status.HTTP_200_OK, data = data)

    @SchemaDefinitions.post_view_put
    def put(self, request, **kwargs):
        """
        Update a post by post_id or author_pk and post_pk.
        """
        if is_remote_access(request):
            return Response(
                status = status.HTTP_403_FORBIDDEN,
                data = {"error": "Remote access is forbidden."}
            )
        post_id = kwargs.get("post_id", None)
        author_pk = kwargs.get("author_pk", None)
        post_pk = kwargs.get("post_pk", None)
        if author_pk and post_pk:
            post_id = LinkGenerator("aap", [author_pk, post_pk]).generate()
        post = get_object_or_404(PostModel, id = post_id)
        if request.user.username != post.author.username:
            return Response(status = status.HTTP_403_FORBIDDEN)
        if request.data["contentType"] not in ["text/plain", "text/markdown"] and request.data.get("content"):
            if not validate_image_file(request.data["content"], request.data["contentType"], mode = "in"):
                return Response(status = status.HTTP_400_BAD_REQUEST, data = {"error": "Unsupported Image Format."})
        serializer = PostSerializer(post, data = request.data, partial = True)
        if not serializer.is_valid():
            return Response(status = status.HTTP_400_BAD_REQUEST, data = serializer.errors)
        serializer.save()
        data = APCLJsonGenerator(request, **kwargs, mode = "post").get_post()
        Outbox(request, data).send()
        return Response(serializer.data, status = status.HTTP_200_OK)

    @SchemaDefinitions.post_view_delete
    def delete(self, request, **kwargs):
        """
        Delete a post by post_id or author_pk and post_pk.
        """
        if is_remote_access(request):
            return Response(
                status = status.HTTP_403_FORBIDDEN,
                data = {"error": "Remote access is forbidden."}
            )
        post_id = kwargs.get("post_id", None)
        author_pk = kwargs.get("author_pk", None)
        post_pk = kwargs.get("post_pk", None)
        if author_pk and post_pk:
            post_id = LinkGenerator("aap", [author_pk, post_pk]).generate()
        post = get_object_or_404(PostModel, id = post_id)
        if request.user.username != post.author.username:
            return Response(status = status.HTTP_403_FORBIDDEN)
        if post.visibility == "DELETED":
            return Response(status = status.HTTP_404_NOT_FOUND)
        post.visibility = "DELETED"
        post.save()
        data = APCLJsonGenerator(request, **kwargs, mode = "post").get_post()
        Outbox(request, data).send()
        return Response(status = status.HTTP_204_NO_CONTENT)

class profileImageView(APIView):

    http_method_names = ['get']
    permission_classes = [AllowAny]

    @SchemaDefinitions.profile_img_get
    def get(self, request, img_id):
        """
        Get the profile image by img_id.
        """
        image_path = os.path.join(settings.MEDIA_ROOT, 'images', 'profile_images', img_id)
        if os.path.exists(image_path):
            return FileResponse(open(image_path, 'rb'))
        else:
            return Response(status = status.HTTP_404_NOT_FOUND)

class PostImageView(APIView):

    http_method_names = ['get']
    permission_classes = [AllowAny]

    @SchemaDefinitions.post_image_view_get
    def get(self, request, **kwargs):
        """
        Get the image of a post by post_id or author_pk and post_pk.
        """
        author_pk = kwargs.get("author_pk", None)
        post_pk = kwargs.get("post_pk", None)
        post_id = kwargs.get("post_id", None)
        if author_pk:
            try: 
                uuid_obj = uuid.UUID(author_pk)
                return Response(status = status.HTTP_404_NOT_FOUND, data = {"detail": "Illegal Image."})
            except ValueError: pass
        if post_id:
            if not post_id.startswith(local_host):
                return Response(status = status.HTTP_404_NOT_FOUND, data = {"detail": "Illegal Image."})
        if author_pk and post_pk:
            post_id = LinkGenerator("aap", [author_pk, post_pk]).generate()
        post = get_object_or_404(PostModel, id = post_id)
        if post.visibility != "PUBLIC" or post.contentType in ["text/plain", "text/markdown"]:
            return Response(status = status.HTTP_404_NOT_FOUND)
        data = validate_image_file(post.content, post.contentType, mode = "out")
        if not data:
            return Response(status = status.HTTP_404_NOT_FOUND)
        return FileResponse(open(data, 'rb'))
    
class APCLJsonGenerator:
    def __init__(self, request, **kwargs):
        self.authors_page = 1
        self.authors_page_size = 10000
        self.comments_page = 1
        self.comments_page_size = 5
        self.likes_page = 1
        self.likes_page_size = 50
        self.authorpg_aloplst = ["authors"]
        self.commentpg_aloplst = ["post", "comments", "commented"]
        self.likepg_aloplst = ["comment", "likes", "liked"]
        self.request = request
        self.author_pk = kwargs.get("author_pk", None)
        self.author_id = kwargs.get("author_id", None)
        self.post_pk = kwargs.get("post_pk", None)
        self.post_id = kwargs.get("post_id", None)
        self.comment_pk = kwargs.get("comment_pk", None)
        self.comment_id = kwargs.get("comment_id", None)
        self.like_pk = kwargs.get("like_pk", None)
        self.like_id = kwargs.get("like_id", None)
        self.mode = kwargs.get("mode", None)
        self.ira = is_remote_access(request)
    
    def author_pagination(self):
        if self.mode not in self.authorpg_aloplst:
            return
        if self.request.query_params.get("page"):
            self.authors_page = int(self.request.query_params.get("page"))
        if self.request.query_params.get("size"):
            self.authors_page_size = int(self.request.query_params.get("size"))
    
    def comment_pagination(self):
        if self.mode not in self.commentpg_aloplst:
            return
        if self.request.query_params.get("page"):
            self.comments_page = int(self.request.query_params.get("page"))
        if self.request.query_params.get("size"):
            self.comments_page_size = int(self.request.query_params.get("size"))
    
    def like_pagination(self):
        if self.mode not in self.likepg_aloplst:
            return
        if self.request.query_params.get("page"):
            self.likes_page = int(self.request.query_params.get("page"))
        if self.request.query_params.get("size"):
            self.likes_page_size = int(self.request.query_params.get("size"))

    def get_authors(self):
        self.author_pagination()
        authors = []
        for author in AuthorModel.objects.all():
            if is_local(author.id) and author.isVerified:
                authors.append(author)
        authors = authors[((self.authors_page - 1) * self.authors_page_size):(self.authors_page * self.authors_page_size)]
        serializer = AuthorSerializer(authors, many = True)
        data = {
            "type": "authors",
            "authors": remove_kvpair(["username", "password", "lastGithubUpdate", "isVerified"], serializer.data)
        }
        return data

    def get_author(self):
        if not self.author_id:
            self.author_id = LinkGenerator("aa", [self.author_pk]).generate()
        author = get_object_or_404(AuthorModel, id = self.author_id)
        serializer = AuthorSerializer(author)
        return remove_kvpair(["username", "password", "lastGithubUpdate", "isVerified"], serializer.data)

    def get_post(self):
        if not self.post_id:
            self.post_id = LinkGenerator("aap", [self.author_pk, self.post_pk]).generate()
        post = get_object_or_404(PostModel, id = self.post_id)
        data = PostSerializer(post).data
        if data["contentType"] not in ["text/plain", "text/markdown"]:
            if not validate_image_file(data["content"], data["contentType"], mode = "in"):
                image_path = os.path.join(settings.BASE_DIR, "static", "img", "invalidImage.png")
                with open(image_path, 'rb') as image_file:
                    default = image_file.read()
                data["content"] = "data:image/jpeg;base64," + base64.b64encode(default).decode("utf-8")
        data["comments"] = self.get_comments()
        data["likes"] = self.get_post_likes()
        data["author"] = remove_kvpair(["username", "password", "lastGithubUpdate", "isVerified"], AuthorSerializer(post.author).data)
        data = remove_kvpair(["mid"], data)
        return data

    def get_comments(self):
        if not self.post_id:
            self.post_id = LinkGenerator("aap", [self.author_pk, self.post_pk]).generate()
        self.comment_pagination()
        post = get_object_or_404(PostModel, id = self.post_id)
        comments = CommentModel.objects.filter(post = post).order_by('-published')
        likeslst = []
        for comment in comments:
            self.comment_id = comment.id
            likeslst.append(self.get_comment_likes())
        src = CommentSerializer(comments, many = True).data
        src = src[((self.comments_page - 1) * self.comments_page_size):(self.comments_page * self.comments_page_size)]
        for i in range(len(src)):
            src[i]["likes"] = likeslst[i + (self.comments_page - 1) * self.comments_page_size]
            src[i]["author"] = remove_kvpair(["username", "password", "lastGithubUpdate", "isVerified"], src[i]["author"])
        src = remove_kvpair(["mid", "post"], src)
        data = {
            "type": "comments",
            "page": LinkGenerator("ap", [post.author.username, post.mid]).generate(),
            "id": LinkGenerator("aapc", [post.author.username, post.mid]).generate(),
            "page_number": self.comments_page,
            "size": self.comments_page_size,
            "count": comments.count(),
            "src": src
        }
        return data
    
    def get_commented(self):
        if not self.author_id:
            self.author_id = LinkGenerator("aa", [self.author_pk]).generate()
        self.comment_pagination()
        comments = CommentModel.objects.filter(author = self.author_id).order_by('-published')
        comments_list = list(comments)
        for comment in comments_list:
                if comment.post.visibility == "DELETED":
                    comments_list.remove(comment)
        if self.ira == True:
            for comment in comments_list:
                if comment.post.visibility == "FRIENDS":
                    comments_list.remove(comment)
        likeslst = []
        for comment in comments_list:
            self.comment_id = comment.id
            likeslst.append(self.get_comment_likes())
        src = CommentSerializer(comments_list, many = True).data
        src = src[((self.comments_page - 1) * self.comments_page_size):(self.comments_page * self.comments_page_size)]
        for i in range(len(src)):
            src[i]["likes"] = likeslst[i + (self.comments_page - 1) * self.comments_page_size]
            src[i]["author"] = remove_kvpair(["username", "password", "lastGithubUpdate", "isVerified"], src[i]["author"])
        src = remove_kvpair(["mid", "post"], src)
        data = {
            "type": "comments",
            "page_number": self.comments_page,
            "size": self.comments_page_size,
            "count": len(comments_list),
            "src": src
        }
        return data

    def get_comment(self):
        if not self.comment_id:
            self.comment_id = LinkGenerator("aac", [self.author_pk, self.comment_pk]).generate()
        comment = get_object_or_404(CommentModel, id = self.comment_id)
        data = CommentSerializer(comment).data
        data["likes"] = self.get_comment_likes()
        data["author"] = remove_kvpair(["username", "password", "lastGithubUpdate", "isVerified"], AuthorSerializer(comment.author).data)
        data = remove_kvpair(["mid", "post"], data)
        return data

    def get_post_likes(self):
        if not self.post_id:
            self.post_id = LinkGenerator("aap", [self.author_pk, self.post_pk]).generate()
        self.like_pagination()
        post = get_object_or_404(PostModel, id = self.post_id)
        likes = LikeModel.objects.filter(post = post).order_by('-published')
        src = LikeSerializer(likes, many = True).data
        src = src[((self.likes_page - 1) * self.likes_page_size):(self.likes_page * self.likes_page_size)]
        for like in src:
            like["author"] = remove_kvpair(["username", "password", "lastGithubUpdate", "isVerified"], like["author"])
        src = remove_kvpair(["mid", "post", "comment"], src)
        data = {
            "type": "likes",
            "page": LinkGenerator("ap", [post.author.username, post.mid]).generate(),
            "id": LinkGenerator("aapl", [post.author.username, post.mid]).generate(),
            "page_number": self.likes_page,
            "size": self.likes_page_size,
            "count": likes.count(),
            "src": src
        }
        return data

    def get_comment_likes(self):
        if not self.comment_id:
            self.comment_id = LinkGenerator("aac", [self.author_pk, self.comment_pk]).generate()
        self.like_pagination()
        comment = get_object_or_404(CommentModel, id = self.comment_id)
        likes = LikeModel.objects.filter(comment = comment).order_by('-published')
        src = LikeSerializer(likes, many = True).data
        src = src[((self.likes_page - 1) * self.likes_page_size):(self.likes_page * self.likes_page_size)]
        for like in src:
            like["author"] = remove_kvpair(["username", "password", "lastGithubUpdate", "isVerified"], like["author"])
        src = remove_kvpair(["mid", "post", "comment"], src)
        data = {
            "type": "likes",
            "page": LinkGenerator("acl", [comment.author.username, comment.mid]).generate(),
            "id": LinkGenerator("aacl", [comment.author.username, comment.mid]).generate(),
            "page_number": self.likes_page,
            "size": self.likes_page_size,
            "count": likes.count(),
            "src": src
        }
        return data
    
    def get_liked(self):
        if not self.author_id:
            self.author_id = LinkGenerator("aa", [self.author_pk]).generate()
        self.like_pagination()
        author = get_object_or_404(AuthorModel, id = self.author_id)
        likes = LikeModel.objects.filter(author = self.author_id).order_by('-published')
        src = LikeSerializer(likes, many = True).data
        src = src[((self.likes_page - 1) * self.likes_page_size):(self.likes_page * self.likes_page_size)]
        for like in src:
            like = remove_kvpair(["mid", "post", "comment"], like)
            like["author"] = remove_kvpair(["username", "password", "lastGithubUpdate", "isVerified"], like["author"])
        data = {
            "type": "likes",
            "page": author.page,
            "id": f"{self.author_id}/likes",
            "page_number": self.likes_page,
            "size": self.likes_page_size,
            "count": likes.count(),
            "src": src
        }
        return data

    def get_like(self):
        if not self.like_id:
            self.like_id = LinkGenerator("aal", [self.author_pk, self.like_pk]).generate()
        like = get_object_or_404(LikeModel, id = self.like_id)
        data = remove_kvpair(["mid", "post", "comment"], LikeSerializer(like).data)
        data["author"] = remove_kvpair(["username", "password", "lastGithubUpdate", "isVerified"], AuthorSerializer(like.author).data)
        return data
      
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