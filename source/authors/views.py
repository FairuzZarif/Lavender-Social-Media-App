from datetime import datetime, timezone
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
from posts.views import *
from posts.serializers import *
from .serializers import *

from django.core.files.storage import default_storage #type: ignore
from django.core.files.base import ContentFile # type: ignore
from rest_framework.utils.serializer_helpers import ReturnDict, ReturnList #type: ignore
import re
import urllib.parse
import uuid, os, requests #type: ignore
import base64
from core.schema_defs import *

local_host = settings.LOCAL_HOST
api_host = settings.API_HOST

""" Author Classes """
class AuthorsView(APIView):

    http_method_names = ['get', 'post']

    def get_permissions(self):
        if self.request.method == "POST":
            return [AllowAny()]
        return [IsAuthenticated()]

    @SchemaDefinitions.authors_view_get
    def get(self, request):
        """
        Get all authors.
        """
        data = APCLJsonGenerator(request, mode = "authors").get_authors()
        return Response(status = status.HTTP_200_OK, data = data)

    @SchemaDefinitions.authors_view_post
    def post(self, request):
        """
        Create a new author.
        """
        if request.data["username"] == "remoteauth":
            return Response(status = status.HTTP_403_FORBIDDEN)
        if AuthorModel.objects.filter(username = request.data["username"]).exists():
            return Response(status = status.HTTP_409_CONFLICT)
        if 'profileImage' in request.data:
            profile_image_name = save_profile_image(request, request.data["username"])
            request.data['profileImage'] = api_host + "profileimage/" + profile_image_name
        serializer = AuthorSerializer(data = request.data, partial = True)
        if not serializer.is_valid():
            return Response(status = status.HTTP_400_BAD_REQUEST, data = serializer.errors)
        author = serializer.save()
        author.id = LinkGenerator("aa", [serializer.data["username"]]).generate()
        author.host = api_host
        author.page = LinkGenerator("a", [serializer.data["username"]]).generate()
        author.save()
        serializer = AuthorSerializer(author)
        data = remove_kvpair(["username", "password", "lastGithubUpdate", "isVerified"], serializer.data)
        return Response(status = status.HTTP_201_CREATED, data = data)

class AuthorView(APIView):

    http_method_names = ['get', 'post', 'put']
    permission_classes = [IsAuthenticated]

    def get_credential(self, node):
        ori = node.outUsername + ":" + node.outPassword
        return base64.b64encode(ori.encode()).decode()
    
    @SchemaDefinitions.author_view_get
    def get(self, request, **kwargs):
        """
        Get a author by author_pk or author_id.
        """
        author_pk = kwargs.get("author_pk", None)
        author_id = kwargs.get("author_id", None)
        
        request_path = request.get_full_path()  # Get full request path
        print(request_path)
        match = re.search(r'(http[s]?://[^\s]+)', request_path)

        if match:
            extracted_url = match.group(1)  # Raw encoded URL
            decoded_url = urllib.parse.unquote(extracted_url)  # Decode URL encoding
            
            shared_nodes = ShareNodeModel.objects.all()
            for shared_node in shared_nodes:
                if decoded_url.startswith(shared_node.host):  # Check if decoded_url starts with shared_node.host
                    print("Match found:", shared_node.host)
                    
                    if not shared_node.allowOut:
                        return
                    
                    url = f"{decoded_url}"

                    headers = {
                        "X-Original-Host": str(self.request.build_absolute_uri("/")) + "api/",
                        "Authorization": f"Basic {self.get_credential(shared_node)}",
                        "Content-Type": "application/json"
                    }

                    try:
                        response = requests.get(url, headers=headers)
                        print(f"Request successful, status code: {response.status_code}")
                        
                        # Ensure the response is a valid JSON object
                        if response.status_code == 200:
                            response_data = response.json()  # Parse the JSON response

                            # Check if the expected data structure is present
                            if isinstance(response_data, dict):
                                return Response(data=response_data, status=status.HTTP_200_OK)
                            else:
                                print(f"Unexpected response structure: {response_data}")
                                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                        else:
                            print(f"Failed to fetch data, status code: {response.status_code}")
                            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                    except requests.exceptions.RequestException as e:
                        print(f"Request failed: {e}")
                        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                    
        if not author_id:
            author_id = LinkGenerator("aa", [author_pk]).generate()
        author = get_object_or_404(AuthorModel, id = author_id)
        if author.isVerified == False:
            return Response(status = status.HTTP_404_NOT_FOUND)
        data = APCLJsonGenerator(request, **kwargs, mode = "author").get_author()
        return Response(status = status.HTTP_200_OK, data = data)

    @SchemaDefinitions.author_view_post
    def post(self, request, author_pk):
        """
        Verify a author by author_pk and password.
        """
        if is_remote_access(request):
            return Response(
                status = status.HTTP_403_FORBIDDEN,
                data = {"error": "Remote access is forbidden."}
            )

        author_id = LinkGenerator("aa", [author_pk]).generate()
        print(author_id)
        author = get_object_or_404(AuthorModel, id = author_id)
        if author.isVerified == False:
            return Response(status = status.HTTP_404_NOT_FOUND)
        if author.password == "!":
            return Response(status = status.HTTP_404_NOT_FOUND)
        serializer = AuthorSerializer(author)
        data = remove_kvpair(["username", "password", "lastGithubUpdate", "isVerified"], serializer.data)
        handle_github_activity(request, author)
        return Response(status = status.HTTP_200_OK, data = data)

    @SchemaDefinitions.author_view_put
    def put(self, request, author_pk):
        """
        Update a author by author_pk.
        """
        if is_remote_access(request):
            return Response(
                status = status.HTTP_403_FORBIDDEN,
                data = {"error": "Remote access is forbidden."}
            )
        if request.user.username != author_pk:
            return Response(status = status.HTTP_403_FORBIDDEN)
        author_id = LinkGenerator("aa", [author_pk]).generate()
        author = get_object_or_404(AuthorModel, id = author_id)
        if author.isVerified == False:
            return Response(status = status.HTTP_404_NOT_FOUND)
        if 'profileImage' in request.data:
            profile_image_name = save_profile_image(request, author_pk)
            request.data['profileImage'] = api_host + "profileimage/" + profile_image_name
        serializer = AuthorSerializer(author, data = request.data, partial = True)
        if not serializer.is_valid():
            return Response(status = status.HTTP_400_BAD_REQUEST, data = serializer.errors)
        serializer.save()
        data = remove_kvpair(["username", "password", "lastGithubUpdate", "isVerified"], serializer.data)
        handle_github_activity(request, author)
        return Response(status = status.HTTP_200_OK, data = data)


""" Stream Classes """

class StreamView(APIView):
    http_method_names = ['get']
    permission_classes = [IsAuthenticated]


    def get(self, request, author_id):
        """
        Get the stream of posts.
        """
        if is_remote_access(request):
            return Response(
                status = status.HTTP_403_FORBIDDEN,
                data = {"error": "Remote access is forbidden."}
            )
        serializer = PostSerializer(
            PostModel.objects.exclude(visibility = "DELETED").order_by('-published'),
            many = True
        )
        posts = []
        if not serializer.data:
            print("hit here")
            return Response(status = status.HTTP_200_OK, data = posts)
        for data in serializer.data:
            print(author_id)
            if stream_legality_verification(author_id, data):
                print("starting handling")
                handle_post_data(author_id, data)
                posts.append(data)
                print(posts)
        return Response(status = status.HTTP_200_OK, data = posts)

def stream_legality_verification(author_id, data):
    """
    Check if the post is legal to be shown in the stream.
    """
    if author_id == data["author"]:
        return True
    if data["visibility"] == "PUBLIC":
        return True
    if data["visibility"] ==  "UNLISTED":
        if isFollowed(author_id, data["author"]):
            return True
    if data["visibility"] == "FRIENDS":
        if isFriend(author_id, data["author"]):
            return True
    return False


class StreamLengthView(APIView):
    http_method_names = ['get']
    permission_classes = [IsAuthenticated]

    def get(self, request, author_id):
        """
        Get the length of the stream of posts.
        """
        
        if is_remote_access(request):
            return Response(
                status = status.HTTP_403_FORBIDDEN,
                data = {"error": "Remote access is forbidden."}
            )
        print("in here")
        serializer = PostSerializer(
            PostModel.objects.exclude(visibility = "DELETED").order_by('-published'),
            many = True
        )
        stream_length = {"stream_length": 0}
        if not serializer.data:
            return Response(status = status.HTTP_200_OK, data = stream_length)
        for data in serializer.data:
            if stream_legality_verification(author_id, data):
                stream_length["stream_length"] += 1
        return Response(status = status.HTTP_200_OK, data = stream_length)

class StreamPostView(APIView):
    http_method_names = ['get']
    permission_classes = [IsAuthenticated]

    def get(self, request, author_id, seq_num):
        """
        Get a specific post from the stream.
        """
        if is_remote_access(request):
            return Response(
                status = status.HTTP_403_FORBIDDEN,
                data = {"error": "Remote access is forbidden."}
            )
        if not seq_num.isdigit():
            return Response(status = status.HTTP_400_BAD_REQUEST)
        serializer = PostSerializer(
            PostModel.objects.exclude(visibility = "DELETED").order_by('-published'),
            many = True
        )
        if not serializer.data or seq_num == 0:
            return Response(status = status.HTTP_404_NOT_FOUND)
        counter = 0
        data = None
        for post in serializer.data:
            if stream_legality_verification(author_id, post):
                counter += 1
            if counter == int(seq_num):
                data = post
                break
        if not data:
            return Response(status = status.HTTP_404_NOT_FOUND)
        handle_post_data(author_id, data)
        return Response(status = status.HTTP_200_OK, data = data)

""" HELPER CLASSES FOR PROFILE IMAGE for author"""
def save_profile_image(request, author_pk):
    profimg_name = standardize_profile_image_name(request.data.get("profileImage"), author_pk)
    profimg_file = request.FILES['profileImage']
    upload_path = os.path.join('images/profile_images', profimg_name)
    default_storage.save(upload_path, ContentFile(profimg_file.read()))
    return profimg_name

def standardize_profile_image_name(profimg, author_pk):
    return f"{author_pk}-{uuid.uuid4()}{profimg.name[profimg.name.rfind('.'):]}"

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
 
""" Github Activity Helpers """
class GithubActivityGenerator:

    def __init__(self, event):
        self.dict = {
            "PushEvent": [2, "Created ", " commit(s) in "],
            "PullRequestEvent": [2, "", " 1 pull request in "],
            "PullRequestReviewEvent": [1, "Reviewed 1 commit in "],
            "IssuesEvent": [2, "", " an issue in "],
            "IssueCommentEvent": [2, "", " an issue comment in "],
            "PullRequestReviewCommentEvent": [1, "Reviewed a comment on a pull request in "],
            "CreateEvent": [2, "Created a ", " - "],
            "DeleteEvent": [2, "Deleted a ", " - "],
            "ReleaseEvent": [1, "Released a tag in "],
            "PublicEvent": [1, "", " is now public"],
            "ForkEvent": [1,  "Fork a repo from: "],
            "WatchEvent": [1, "Started to watch: "]
        }
        self.event = event
        self.mode = event["type"]
        self.args = []
        self.returnee = ""

    def set_args(self):
        if self.mode == "PushEvent":
            self.args.append(self.event["payload"]["size"])
            self.args.append(self.event["repo"]["name"])
        elif self.mode == "PullRequestEvent":
            self.args.append(self.event["payload"]["action"].capitalize())
            self.args.append(self.event["repo"]["name"])
        elif self.mode == "PullRequestReviewEvent":
            self.args.append(self.event["repo"]["name"])
        elif self.mode == "PullRequestReviewCommentEvent":
            self.args.append(self.event["repo"]["name"])
        elif self.mode == "IssuesEvent":
            self.args.append(self.event["payload"]["action"].capitalize())
            self.args.append(self.event["repo"]["name"])
        elif self.mode == "IssueCommentEvent":
            self.args.append(self.event["payload"]["action"].capitalize())
            self.args.append(self.event["repo"]["name"])
        elif self.mode == "CreateEvent":
            self.args.append(self.event["payload"]["ref_type"])
            self.args.append(self.event["repo"]["name"])
        elif self.mode == "DeleteEvent":
            self.args.append(self.event["payload"]["ref_type"])
            self.args.append(self.event["repo"]["name"])
        elif self.mode == "ReleaseEvent":
            self.args.append(self.event["payload"]["action"].capitalize())
            self.args.append(self.event["repo"]["name"])
        elif self.mode == "ForkEvent":
            self.args.append(self.event["repo"]["name"])
        elif self.mode == "WatchEvent":
            self.args.append(self.event["repo"]["name"])

    def merge(self):
        args_len = len(self.args)
        modelst = self.dict[self.mode]
        modelst.pop(0)
        modelst_len = len(modelst)
        counter = 0
        while counter < args_len or counter < modelst_len:
            if counter < modelst_len:
                self.returnee += str(modelst[counter])
            if counter < args_len:
                self.returnee += str(self.args[counter])
            counter += 1

    def generate(self):
        self.set_args()
        self.merge()
        return self.returnee

def handle_github_activity(request, author):
    if not author.github:
        return
    github_username = author.github.split("/")[-1]
    github_api = f"https://api.github.com/users/{github_username}/events/public"
    response = requests.get(github_api)
    if response.status_code != 200:
        return
    availble_types = [
        "PushEvent", "PullRequestEvent", "PullRequestReviewEvent", "PullRequestReviewCommentEvent",
        "IssuesEvent", "DeleteEvent", "CreateEvent", "ReleaseEvent", "PublicEvent", "ForkEvent", "WatchEvent"
    ]
    events = response.json()
    events.reverse()
    for event in events:
        standardized_created_at = datetime.strptime(event["created_at"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo = timezone.utc)
        if (standardized_created_at < author.lastGithubUpdate
            or event["type"] not in availble_types):
            continue
        content = GithubActivityGenerator(event).generate()
        data = {
            "title": "Github Update " + event["created_at"],
            "description": event["type"],
            "contentType": "text/plain",
            "content": content,
            "published": event["created_at"],
            "visibility": "PUBLIC"
        }
        serializer = PostSerializer(data = data, partial = True)
        if not serializer.is_valid():
            continue
        post = serializer.save(author = author)
        post.id = LinkGenerator("aap", [author.username, post.mid]).generate()
        post.save()
        data = APCLJsonGenerator(request, post_id = post.id, mode = "post").get_post()
        Outbox(request, data).send()
    author.lastGithubUpdate = datetime.now(timezone.utc)
    author.save()

""""  VERY IMPORTANT HELPER CLASSES UNDER HERE      """
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
