from authors.serializers import AuthorSerializer
from drf_spectacular.extensions import OpenApiAuthenticationExtension
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, OpenApiRequest, OpenApiResponse
from authors.serializers import *
from posts.serializers import *
from follow.serializers import *
from comments_likes.serializers import *

class LavenderAuthExtension(OpenApiAuthenticationExtension):
    target_class = 'core.authentication.LavenderAuth'
    name = 'LavenderAuth'
    def get_security_definition(self, auto_schema):
        return {
            'type': 'http',
            'scheme': 'bearer',
            'bearerFormat': 'JWT',
        }

OpenApiAuthenticationExtension.register(LavenderAuthExtension)

class SchemaDefinitions:
    """authors_view class"""
    authors_view_get = extend_schema(
        operation_id = "authors_view_get",
        summary = "Retrieve all authors",
        description = """
            Retrieve a list of all authors registered in the system.
            - Authentication: Required.
            - Permissions: Authenticated users can retrieve the list of authors.
        """,
        parameters = [
            OpenApiParameter(
                name = "page",
                type = OpenApiTypes.INT,
                location = OpenApiParameter.QUERY,
                description = "Page number for pagination."
            ),
            OpenApiParameter(
                name = "size",
                type = OpenApiTypes.INT,
                location = OpenApiParameter.QUERY,
                description = "Number of authors per page."
            ),
        ],
        responses = {
            200: OpenApiResponse(
                response = AuthorSerializer(many = True),
                description = "A list of authors.",
                examples = [
                    OpenApiExample(
                        "Successful Response",
                        value = {
                            "type": "authors",
                            "authors": [
                                {   
                                    "type": "author",
                                    "id": "http://socialapp/api/authors/abc",
                                    "display_name": "ABC",
                                    "page": "http://socialapp/authors/abc",
                                    "github": "https://github.com/abc",
                                    "profile_image": "http://socialapp/images/abc.jpg"
                                },
                                {
                                    "type": "author",
                                    "id": "http://socialapp/api/authors/def",
                                    "display_name": "DEF",
                                    "page": "http://socialapp/authors/def",
                                    "github": "https://github.com/def",
                                    "profile_image": "http://socialapp/images/def.jpg"
                                },
                            ]
                        }
                    )
                ],
            ),
            401: OpenApiResponse(description = "Unauthorized"),
        },
        tags = ["Authors"],
    )

    authors_view_post = extend_schema(
        operation_id = "authors_view_post",
        summary = "Create a new author",
        description = """
            Register a new author in the system.
            - Authentication: Not required.
            - Permissions: Anyone can create a new author account.
        """,
        request = OpenApiRequest(
                request = AuthorSerializer,
                examples = [
                    OpenApiExample(
                        "Example Request",
                        value = {
                            "username": "abc",
                            "password": "123"
                        }
                    )
                ],
            ),
        responses = {
            201: OpenApiResponse(
                response = AuthorSerializer,
                description = "Author created successfully.",
                examples = [
                    OpenApiExample(
                        "Successful Response",
                        value = {
                            "type": "author",
                            "id": "http://socialapp/api/authors/abc",
                            "display_name": "ABC",
                            "page": "http://socialapp/authors/abc",
                            "github": "https://github.com/abc",
                            "profile_image": "http://socialapp/images/abc.jpg"
                        }
                    )
                ],
            ),
            400: OpenApiResponse(description = "Bad Request"),
            409: OpenApiResponse(description = "Conflict"),
        },
        tags = ["Authors"],
    )
    
    
    """author_view class"""
    author_view_get = extend_schema(
        operation_id = "author_view_get",
        summary = "Retrieve a specific author",
        description = """
            Get the details of an author by their primary key (`author_pk`) or ID (`author_id`).
            - Authentication: Required.
            - Permissions: Authenticated users can access their own details.
        """,
        parameters = [
            OpenApiParameter(
                name = "author_pk",
                type = OpenApiTypes.STR,
                location = OpenApiParameter.PATH,
                description = "The primary key (username) of the author."
            ),
            OpenApiParameter(
                name = "author_id",
                type = OpenApiTypes.STR,
                location = OpenApiParameter.PATH,
                description = "The ID of the author."
            ),
        ],
        responses = {
            200: OpenApiResponse(
                response = AuthorSerializer,
                description = "Author details retrieved successfully.",
                examples = [
                    OpenApiExample(
                        "Successful Response",
                        value = {
                            "type": "author",
                            "id": "http://socialapp/api/authors/abc",
                            "display_name": "ABC",
                            "page": "http://socialapp/authors/abc",
                            "github": "https://github.com/abc",
                            "profile_image": "http://socialapp/images/abc.jpg"
                        }
                    )
                ],
            ),
            403: OpenApiResponse(description = "Forbidden"),
            404: OpenApiResponse(description = "Not Found"),
        },
        tags = ["Author"],
    )

    author_view_post = extend_schema(
        operation_id = "author_view_post",
        summary = "Verify author credentials",
        description = """
            Verify an author's credentials by providing their password.
            - Authentication: Required.
            - Permissions: Authenticated users can verify credentials for their own account.
        """,
        request = OpenApiRequest(
                request = AuthorSerializer,
                examples = [
                    OpenApiExample(
                        "Example Request",
                        value = {
                            "username": "abc",
                            "password": "123"
                        }
                    )
                ],
            ),
        responses = {
            200: OpenApiResponse(
                response = AuthorSerializer,
                description = "Credentials verified successfully.",
                examples = [
                    OpenApiExample(
                        "Successful Response",
                        value = {
                            "type": "author",
                            "id": "http://socialapp/api/authors/abc",
                            "display_name": "ABC",
                            "page": "http://socialapp/authors/abc",
                            "github": "https://github.com/abc",
                            "profile_image": "http://socialapp/images/abc.jpg"
                        }
                    )
                ],
            ),
            401: OpenApiResponse(description = "Unauthorized"),
            404: OpenApiResponse(description = "Not Found"),
        },
        tags = ["Author"],
    )

    author_view_put = extend_schema(
        operation_id = "author_view_put",
        summary = "Update author details",
        description = """
            Update the details of an existing author.
            - Authentication: Required.
            - Permissions: Authenticated users can update their own details.
        """,
        request = OpenApiRequest(
                request = AuthorSerializer,
                examples = [
                    OpenApiExample(
                        "Example Request",
                        value = {
                            "type": "author",
                            "id": "http://socialapp/api/authors/abc",
                            "display_name": "ABC",
                            "page": "http://socialapp/authors/abc",
                            "github": "https://github.com/abc",
                            "profile_image": "http://socialapp/images/abc.jpg"
                        }
                    )
                ],
            ),
        responses = {
            200: OpenApiResponse(
                response = AuthorSerializer,
                description = "Author updated successfully.",
                examples = [
                    OpenApiExample(
                        "Successful Response",
                        value = {
                            "type": "author",
                            "id": "http://socialapp/api/authors/abc",
                            "display_name": "ABC",
                            "page": "http://socialapp/authors/abc",
                            "github": "https://github.com/abc",
                            "profile_image": "http://socialapp/images/abc.jpg"
                        }
                    )
                ],
            ),
            400: OpenApiResponse(description = "Bad Request"),
            404: OpenApiResponse(description = "Not Found"),
        },
        tags = ["Author"],
    )

    """profile_image_view class"""
    profile_img_get = extend_schema(
        operation_id = "profile_img_get",
        summary = "retrive the profile image of an author",
        description = """
            retrive the profile image of an author, by this it can be hosted in different node
        """,
        parameters = [
            OpenApiParameter(
                name = "img_id",
                type = OpenApiTypes.STR,
                location = OpenApiParameter.PATH,
                description = "id of the profile image, it include the type such as .jpg",
            ),
        ],
        responses = {
            200: OpenApiResponse(
                description = "return the image file.",
                examples = [
                    OpenApiExample(
                        "Successful Response",
                        value = {
                            "proflie.jpg"
                        }
                    )
                ],
            ),
            404: OpenApiResponse(description = "Profile image Not Found"),
        },
        tags = ["ProfileImage"],
    )

    """inbox_view class"""
    inbox_view_post = extend_schema(
        operation_id = "inbox_view_get",
        summary = "The inbox of node",
        description = """
            The inbox receives all the new posts from followed remote authors, as well as "follow requests," likes, and comments that should be aware of.
            When sending/updating posts, body is a post object
            When sending/updating comments, body is a comment object
            When sending/updating likes, body is a like object
            When sending/updating follow requests, body is a follow object
        """,
        parameters = [
            OpenApiParameter(
                name = "author_pk",
                type = OpenApiTypes.STR,
                location = OpenApiParameter.PATH,
                description = "The primary key (username) of the author."
            ),
        ],
        request = OpenApiRequest(
                request = FollowRequestSerializer,
                examples = [
                    OpenApiExample(
                        "Example follow Request",
                        value = {
                            'type': 'follow',
                            'summary': 'bob want to follow ana',
                            'actor': {
                                'type': 'author',
                                'id': 'http://anotherserver/api/authors/bob',
                                'host': 'http://anotherserver/api/',
                                'displayName': 'bob',
                                'github': '',
                                'page': '',
                                'profileImage': '',
                            },
                            'object': {
                                'type': 'author',
                                'id': 'http://testserver/api/authors/ana',
                                'host': 'http://testserver/api/',
                                'displayName': 'ana',
                                'github': '',
                                'page': '',
                                'profileImage': '',
                            }
                        }
                    ),
                    OpenApiExample(
                        "Example post",
                        value = {
                            'type': 'post',
                            'title': 'A post from others',
                            'id': 'http://anotherserver/api/authors/bob/posts/1',
                            'description': 'its a post',
                            'contentType': 'text/plain',
                            'content': 'the content of my remote post',
                            'author': {
                                'type': 'author',
                                'id': 'http://anotherserver/api/authors/bob',
                                'host': 'http://anotherserver/api/',
                                'displayName': 'bob',
                                'github': '',
                                'page': '',
                                'profileImage': '',
                            },
                            'published': '2015-03-09T13:07:04+00:00',
                            'visibility': 'PUBLIC'
                        }
                    ),
                    OpenApiExample(
                        "Example comment",
                        value = {
                            'type': 'comment',
                            'comment': 'its a comment',
                            'author': {
                                'type': 'author',
                                'id': 'http://anotherserver/api/authors/bob',
                                'host': 'http://anotherserver/api/',
                                'displayName': 'bob',
                                'github': '',
                                'page': '',
                                'profileImage': '',
                            },
                            'contentType': 'text/markdown',
                            'published': '2015-03-09T13:07:04+00:00',
                            'id': 'http://anotherserver/api/authors/bob/commented/1',
                            'post': "http://anotherserver/api/authors/bob/posts/1"
                        }
                    ),
                    OpenApiExample(
                        "Example like",
                        value = {
                            'type': 'like',
                            'author': {
                                'type': 'author',
                                'id': 'http://anotherserver/api/authors/bob',
                                'host': 'http://anotherserver/api/',
                                'displayName': 'bob',
                                'github': '',
                                'page': '',
                                'profileImage': '',
                            },
                            'published': '2015-03-09T13:07:04+00:00',
                            'id': 'http://anotherserver/api/authors/bob/liked/1',
                            'object': 'http://anotherserver/api/authors/bob/posts/1'
                        }
                    )
                ],
            ),
        responses = {
            200: OpenApiResponse(description = "inbox received"),
            400: OpenApiResponse(description = "bad request"),
            403: OpenApiResponse(description = "wrong node username/passward or node reject connection"),
        },
        tags = ["Inbox"]
    )


    following_view_get = extend_schema(
        operation_id = "following_view_get",
        summary = "Get all following authors for current author serial",
        description = """
            Get a list of following authors for a specific author identified by their primary key (serial).
            The response contains a list of following authors (object) for the specified author.
        """,
        parameters = [
            OpenApiParameter(
                name = "author_pk",
                type = OpenApiTypes.STR,
                location = OpenApiParameter.PATH,
                description = "Primary key (serial) of the author",
            ),
        ],
        responses = {
            200: OpenApiResponse(
                response = FollowerSerializer(many = True),
                description = "Successfully retrieved the list of following authors",
                examples = [
                    OpenApiExample(
                        "Example Following Response",
                        value = {
                            "type": "following",
                            "following": [
                                {   
                                    "type": "author",
                                    "id": "http://example.com/api/authors/1",
                                    "display_name": "author 1",
                                    "page": "http://example.com/authors/1",
                                    "github": "https://github.com/1",
                                    "profile_image": "http://example.com/images/1.jpg"
                                },
                                {   
                                    "type": "author",
                                    "id": "http://example.com/api/authors/2",
                                    "display_name": "author 2",
                                    "page": "http://example.com/authors/2",
                                    "github": "https://github.com/2",
                                    "profile_image": "http://example.com/images/2.jpg"
                                }
                            ]
                        }
                    )
                ]
            ),
            404: OpenApiResponse(description = "Author not found"),
        },
        tags = ["Following"]
    )

    followers_view_get = extend_schema(
        operation_id = "followers_view_get",
        summary = "Retrieve all followers of a specific author",
        description = """
            Get a list of followers for a specific author identified by their primary key (serial).
            The response contains a list of followers (actor) for the specified author.
        """,
        parameters = [
            OpenApiParameter(
                name = "author_pk",
                type = OpenApiTypes.STR,
                location = OpenApiParameter.PATH,
                description = "Primary key (serial) of the author",
            ),
        ],
        responses = {
            200: OpenApiResponse(
                response = FollowerSerializer(many = True),
                description = "Successfully retrieved the list of followers",
                examples = [
                    OpenApiExample(
                        "Example Followers Response",
                        value = {
                            "type": "followers",
                            "followers": [
                                {
                                    "type": "author",
                                    "id": "http://example.com/api/authors/1",
                                    "display_name": "author 1",
                                    "page": "http://example.com/authors/1",
                                    "github": "https://github.com/1",
                                    "profile_image": "http://example.com/images/1.jpg"
                                },
                                {
                                    "type": "author",
                                    "id": "http://example.com/api/authors/1",
                                    "display_name": "author 1",
                                    "page": "http://example.com/authors/1",
                                    "github": "https://github.com/1",
                                    "profile_image": "http://example.com/images/1.jpg"
                                }
                            ]
                        }
                    )
                ]
            ),
            404: OpenApiResponse(description = "Author not found"),
        },
        tags = ["Followers"]
    )

    follower_remote_view_get = extend_schema(
        operation_id = "follower_remote_view_get",
        summary = "Check if the current author is a follower of a remote author",
        description = """
            Check if the current author (actor_pk) is following a remote author (object_id)
        """,
        parameters = [
            OpenApiParameter(
                name = "actor_pk",
                type = OpenApiTypes.STR,
                location = OpenApiParameter.PATH,
                description = "primary key of the current author (follower)",
            ),
            OpenApiParameter(
                name = "object_id",
                type = OpenApiTypes.STR,
                location = OpenApiParameter.PATH,
                description = "id of the remote author (followee)",
            )
        ],
        responses = {
            200: OpenApiResponse(response = OpenApiTypes.OBJECT, description = "The specified author is a follower"),
            404: OpenApiResponse(description = "The specified author is not a follower"),
            403: OpenApiResponse(description = "Forbidden access")
        },
        tags = ["Follower"]
    )

    follower_view_get = extend_schema(
        operation_id = "follower_view_get",
        summary = "Check if an author is a follower",
        description = """
            Check if a specific author is following the current author (serial)
        """,
        parameters = [
            OpenApiParameter(
                name = "actor_pk",
                type = OpenApiTypes.STR,
                location = OpenApiParameter.PATH,
                description = "primary key of the current author (who is being followed)",
            ),
            OpenApiParameter(
                name = "object_id",
                type = OpenApiTypes.STR,
                location = OpenApiParameter.PATH,
                description = "id of the follower to check",
            )
        ],
        responses = {
            200: OpenApiResponse(response = OpenApiTypes.OBJECT, description = "The specified author is a follower"),
            404: OpenApiResponse(description = "The specified author is not a follower"),
            403: OpenApiResponse(description = "Forbidden access")
        },
        tags = ["Follower"]
    )

    follower_view_put = extend_schema(
        operation_id = "follower_view_put",
        summary = "Add a follower",
        description = """
            Add a specific author (author_id) as a follower to the current author's (author_pk) followers list.
            - Requires authentication.
        """,
        parameters = [
            OpenApiParameter(
                name = "author_pk",
                type = OpenApiTypes.STR,
                location = OpenApiParameter.PATH,
                description = "primary key of the current author (who is being followed)",
            ),
            OpenApiParameter(
                name = "author_id",
                type = OpenApiTypes.STR,
                location = OpenApiParameter.PATH,
                description = "primary key of the follower to add",
            )
        ],
        request = None,
        responses = {
            201: OpenApiResponse(response = OpenApiTypes.OBJECT, description = "Follower successfully added"),
            400: OpenApiResponse(description = "Invalid request data"),
            401: OpenApiResponse(description = "Unauthorized access")
        },
        tags = ["Follower"]
    )

    follower_view_delete = extend_schema(
        operation_id = "follower_view_delete",
        summary = "Remove a follower",
        description = """
            Remove a specific follower (author_id) from the current author's (author_pk) followers list. 
            - Requires authentication.
        """,
        parameters = [
            OpenApiParameter(
                name = "author_pk",
                type = OpenApiTypes.STR,
                location = OpenApiParameter.PATH,
                description = "primary key of the current author (who is being followed)",
            ),
            OpenApiParameter(
                name = "author_id",
                type = OpenApiTypes.STR,
                location = OpenApiParameter.PATH,
                description = "primary key of the follower to remove",
            )
        ],
        request = None,
        responses = {
            204: OpenApiResponse(response = OpenApiTypes.OBJECT, description = "Follower successfully removed"),
            401: OpenApiResponse(description = "Unauthorized access")
        },
        tags = ["Follower"]
    )

    follow_requests_object_end_get = extend_schema(
        operation_id = "get_follow_request",
        summary = "Get all follow requests for the author",
        description = """
            Get all follow requests for the current author. It will return a request
            list, which each item is a dictionary. The key of the dictionary is the id
            of the follower, and the value is the summary of the request (i.e., who 
            wants to follow who), which is also the reuqest message.
        """,
        parameters = [
            OpenApiParameter(
                name = "author_pk",
                type = OpenApiTypes.STR,
                location = OpenApiParameter.PATH,
                description = "Primary key (serial) of the author",
            ),
        ],
        responses = {
            200: OpenApiResponse(
                response = OpenApiTypes.OBJECT,
                description = "Successfully obtained follow requests",
                examples = [
                    OpenApiExample(
                        "Successful Response",
                        value = {
                            "requests": [
                                {"http://socialapp/api/authors/abc": "abc wants to follow efg"},
                                {"http://socialapp/api/authors/cba": "cba wants to follow efg"}
                            ]
                        } 
                    )
                ]
            )
        },
        tags = ["Follow Request"]                       
    )

    follow_request_object_end_post = extend_schema(
        operation_id = "follow_request_object_end_post",
        summary = "accept the follow request",
        description = """
            The object(author that being followed) that choose to accept. 
            Since the follwer object is already created, then just delete the followreq model
        """,
        parameters = [
            OpenApiParameter(
                name = "object_pk",
                type = OpenApiTypes.STR,
                location = OpenApiParameter.PATH,
                description = "primary key (Serial) of the author",
            ),
        ],
        request = None,
        responses = {
            200: OpenApiResponse(description = "the follow request accepted"),
            403: OpenApiResponse(description = "Forbidden"),
            404: OpenApiResponse(description = "no author or follow request exist"),
        },
        tags = ["Follow Request"] 
    )

    follow_request_object_end_delete = extend_schema(
        operation_id = "follow_request_object_end_delete",
        summary = "reject the follow request",
        description = """
            The object(author that being followed) that choose to reject. 
            delete the followreq model and follower model at the same time
        """,
        parameters = [
            OpenApiParameter(
                name = "object_pk",
                type = OpenApiTypes.STR,
                location = OpenApiParameter.PATH,
                description = "primary key (Serial) of the author",
            ),
        ],
        request = None,
        responses = {
            204: OpenApiResponse(description = "the follow request rejected"),
            403: OpenApiResponse(description = "Forbidden"),
            404: OpenApiResponse(description = "no author or follow request exist"),
        },
        tags = ["Follow Request"] 
    )

    follow_request_actor_end_post = extend_schema(
        operation_id = "handle_follow_request_post",
        summary = "Send follow request to a specific user",
        description = """
            Send a follow request from actor_pk to object_id. Here object_id 
            refers to the id who is going to be followed, and actor_pk 
            refers to the primary key of the current user. Once the follow request
            is created, the followee (from the other end) can be notified.
        """,
        parameters = [
            OpenApiParameter(
                name = "actor_pk",
                type = OpenApiTypes.STR,
                location = OpenApiParameter.PATH,
                description = "Primary key (serial) of the author",
            ),
            OpenApiParameter(
                name = "object_id",
                type = OpenApiTypes.STR,
                location = OpenApiParameter.PATH,
                description = "Id (FQID) of the followee",
            ),
        ],
        request = None,
        responses = {
            201: OpenApiResponse(response=OpenApiTypes.OBJECT, description = "Created"),
        },
        tags = ["Follow Request"] 
    )

    follow_request_actor_end_delete = extend_schema(
        operation_id = "handle_follow_request_delete",
        summary = "Delete a follow request someone sended to the current user",
        description = """
            Delete a follow request object_id sent to actor_pk. Here object_id 
            refers to the id of the user who sent the request, and actor_pk 
            refers to the primary key of the current user. Once the follow request
            is deleted, the end of object should not receive any unlisted posts
            made by current user.
        """,
        parameters = [
            OpenApiParameter(
                name = "actor_pk",
                type = OpenApiTypes.STR,
                location = OpenApiParameter.PATH,
                description = "Primary key (serial) of the author",
            ),
            OpenApiParameter(
                name = "object_id",
                type = OpenApiTypes.STR,
                location = OpenApiParameter.PATH,
                description = "Id (FQID) of the follower",
            ),
        ],
        responses = {
            404: OpenApiResponse(description = "Not Found"),
        },
        tags = ["Follow Request"] 
    )

    stream_view_get = extend_schema(
        operation_id = "stream_view_get",
        summary = "Get all newest posts posted by node users",
        description = """
            It will present all public posts, all friends posts, all posts 
            made by current following, and all posts made by current user. Github
            activities are also available.
        """,
        parameters = [
            OpenApiParameter(
                name = "author_id",
                type = OpenApiTypes.STR,
                location = OpenApiParameter.PATH,
                description = "Primary key (serial) of the author",
            ),
        ],
        responses = {
            200: OpenApiResponse(
                response = PostSerializer,
                description = "Successfully obtained posts",
                examples = [
                    OpenApiExample(
                        "Successful Response",
                        value = {
                            "type": "post",
                            "title": "Sample Post",
                            "id": "http://socialapp/api/authors/abc/posts/1",
                            "description": "You're seeing a sample",
                            "content": "This is a sample post content",
                            "contentTypes": "Plain Text",
                            "page": "http://socialapp/authors/abc/posts/1",
                            "author": {
                                "type": "author",
                                "id": "http://socialapp/api/authors/abc",
                                "display_name": "ABC",
                                "page": "http://socialapp/authors/abc",
                                "github": "https://github.com/abc",
                                "profile_image": "http://socialapp/images/abc.jpg"
                            },
                            "published":"2024-10-20T14:30:00Z",
                            "visibility": "PUBLIC",
                        }
                    )
                ]
            )
        },
        tags = ["Stream"]      
    )

    stream_length_view_get = extend_schema(
        operation_id = "stream_length_view_get",
        summary = "get the length of current stream",
        description = """
            get the length of current stream
        """,
        parameters = [
            OpenApiParameter(
                name = "author_id",
                type = OpenApiTypes.STR,
                location = OpenApiParameter.PATH,
                description = "id (fqid) of the author",
            ),
        ],
        responses = {
            200: OpenApiResponse(
                description = "Successfully obtained the num of posts in stream ",
                examples = [
                    OpenApiExample(
                        "Successful Response",
                        value = 3
                    )
                ]
            )
        },
        tags = ["Stream"]    
    )

    stream_post_view_get = extend_schema(
        operation_id = "stream_post_view_get",
        summary = "get one spec post by it's sequence",
        description = """
            get one spec post by it's sequence
        """,
        parameters = [
            OpenApiParameter(
                name = "author_id",
                type = OpenApiTypes.STR,
                location = OpenApiParameter.PATH,
                description = "id (fqid) of the author",
            ),
            OpenApiParameter(
                name = "seq_num",
                type = OpenApiTypes.STR,
                location = OpenApiParameter.PATH,
                description = "sequence of this post in stream",
            ),
        ],
        responses = {
            200: OpenApiResponse(
                response = PostSerializer,
                description = "Successfully retrived",
                examples = [
                    OpenApiExample(
                        "Successful Response",
                        value = {
                            "type": "post",
                            "title": "Sample Post",
                            "id": "http://socialapp/api/authors/abc/posts/1",
                            "description": "You're seeing a sample",
                            "content": "This is a sample post content",
                            "contentTypes": "Plain Text",
                            "page": "http://socialapp/authors/abc/posts/1",
                            "author": {
                                "type": "author",
                                "id": "http://socialapp/api/authors/abc",
                                "display_name": "ABC",
                                "page": "http://socialapp/authors/abc",
                                "github": "https://github.com/abc",
                                "profile_image": "http://socialapp/images/abc.jpg"
                            },
                            "published":"2024-10-20T14:30:00Z",
                            "visibility": "PUBLIC",
                            
                        }
                    )
                ]
            ),
            400: OpenApiResponse(description = "bad request, seq num is not a int"),
            404: OpenApiResponse(description = "post not found"),
        },
        tags = ["Stream"]    
    )
    
    posts_view_get = extend_schema(
        operation_id = "posts_view_get",
        summary = "Retrieve posts for a specific author",
        description = """
            Get posts created by a specific author. If the user is the author, 
            all posts will be returned. If the user is a friend, only public 
            and friends-only posts will be visible. If the user is a stranger, 
            only public posts will be returned.
            - Authentication: Optional for public posts.
            - Permissions: Authenticated users can view more restricted posts.
        """,
        parameters = [
            OpenApiParameter(
                name = "author_pk",
                type = OpenApiTypes.STR,
                location = OpenApiParameter.PATH,
                description = "Primary key (serial) of the author",
            ),
        ],
        responses = {
            200: OpenApiResponse(
                response = PostSerializer,
                description = "Successfully retrieved posts",
                examples = [
                    OpenApiExample(
                        "Successful Response",
                        value = [
                            {
                                "type": "post",
                                "title": "Sample Post",
                                "id": "http://socialapp/api/authors/abc/posts/1",
                                "description": "You're seeing a sample",
                                "content": "This is a sample post content",
                                "contentTypes": "Plain Text",
                                "page": "http://socialapp/authors/abc/posts/1",
                                "author": {
                                    "type": "author",
                                    "id": "http://socialapp/api/authors/abc",
                                    "display_name": "ABC",
                                    "page": "http://socialapp/authors/abc",
                                    "github": "https://github.com/abc",
                                    "profile_image": "http://socialapp/images/abc.jpg"
                                },
                                "published": "2024-10-20T14:30:00Z",
                                "visibility": "PUBLIC",
                            },
                            {
                                "type": "post",
                                "title": "Sample Post",
                                "id": "http://socialapp/api/authors/abc/posts/2",
                                "description": "You're seeing a sample",
                                "content": "This is a sample post content",
                                "contentTypes": "Plain Text",
                                "page": "http://socialapp/authors/abc/posts/2",
                                "author": {
                                    "type": "author",
                                    "id": "http://socialapp/api/authors/abc",
                                    "display_name": "ABC",
                                    "apge": "http://socialapp/authors/abc",
                                    "github": "https://github.com/abc",
                                    "profile_image": "http://socialapp/images/abc.jpg"
                                },
                                "published": "2024-10-20T14:30:00Z",
                                "visibility": "PUBLIC",
                            }
                        ]
                    )
                ]
            ),
            403: OpenApiResponse(description = "Permission denied"),
            404: OpenApiResponse(description = "Author not found"),
        },
        tags = ["Post"]
    )

    posts_view_post = extend_schema(
        operation_id = "posts_view_post",
        summary = "Create a new post for a specific author",
        description = """
            Create a new post under a specific author's profile.
            - Authentication: Required.
            - Permissions: Only authenticated users can create posts.
        """,
        parameters = [
            OpenApiParameter(
                name = "author_pk",
                type = OpenApiTypes.STR,
                location = OpenApiParameter.PATH,
                description = "Primary key (serial) of the author",
            ),
        ],
        request = OpenApiRequest(
                request = PostSerializer,
                examples = [
                    OpenApiExample(
                        "Example Request",
                        value = {
                            "title": "Sample Post",
                            "description": "You're seeing a sample",
                            "content": "This is a sample post content",
                            "contentTypes": "Plain Text",
                            "visibility": "PUBLIC",
                        }
                    )
                ],
            ),
        responses = {
            201: OpenApiResponse(
                response = PostSerializer,
                description = "Post created successfully",
                examples = [
                    OpenApiExample(
                        "Successful Response",
                        value = {
                                "type": "post",
                                "title": "Sample Post",
                                "id": "http://socialapp/api/authors/abc/posts/1",
                                "description": "You're seeing a sample",
                                "content": "This is a sample post content",
                                "contentTypes": "Plain Text",
                                "page": "http://socialapp/authors/abc/posts/1",
                                "author": {
                                    "type": "author",
                                    "id": "http://socialapp/api/authors/abc",
                                    "display_name": "ABC",
                                    "page": "http://socialapp/authors/abc",
                                    "github": "https://github.com/abc",
                                    "profile_image": "http://socialapp/images/abc.jpg"
                                },
                                "published":"2024-10-20T14:30:00Z",
                                "visibility": "PUBLIC",
                            }
                    )
                ]
            ),
            400: OpenApiResponse(description = "Invalid post data"),
            404: OpenApiResponse(description = "Author not found"),
        },
        tags = ["Post"]
    )

    post_view_get = extend_schema(
        operation_id = "post_view_get",
        summary = "Retrieve a specific post",
        description = """
            Get a specific post with detailed information such as comments and likes.
        """,
        parameters = [
            OpenApiParameter(
                name = "author_mid",
                type = OpenApiTypes.STR,
                location = OpenApiParameter.PATH,
                description = "Primary key (serial) of the author",
            ),
            OpenApiParameter(
                name = "post_mid",
                type = OpenApiTypes.STR,
                location = OpenApiParameter.PATH,
                description = "Primary key (serial) of the post",
            )
        ],
        responses = {
            200: OpenApiResponse(
                response = PostSerializer,
                description = "Successfully retrieved post",
                examples = [
                    OpenApiExample(
                        "Successful Response",
                        value = {
                            "type": "post",
                            "title": "Sample Post",
                            "id": "http://socialapp/api/authors/abc/posts/1",
                            "description": "You're seeing a sample",
                            "content": "This is a sample post content",
                            "contentTypes": "Plain Text",
                            "page": "http://socialapp/authors/abc/posts/1",
                            "author": {
                                "type": "author",
                                "id": "http://socialapp/api/authors/abc",
                                "display_name": "ABC",
                                "page": "http://socialapp/authors/abc",
                                "github": "https://github.com/abc",
                                "profile_image": "http://socialapp/images/abc.jpg"
                            },
                            "published":"2024-10-20T14:30:00Z",
                            "visibility": "PUBLIC",
                            
                        }
                    )
                ]
            ),
            404: OpenApiResponse(description = "Post not found"),
            403: OpenApiResponse(description = "Permission denied"),
        },
        tags = ["Post"],
    )

    post_view_put = extend_schema(
        operation_id = "post_view_put",
        summary = "Update a specific post",
        description = """
            Update the content of a specific post. Only the post author can update the post.
        """,
        parameters = [
            OpenApiParameter(
                name = "author_mid",
                type = OpenApiTypes.STR,
                location = OpenApiParameter.PATH,
                description = "Primary key (serial) of the author",
            ),
            OpenApiParameter(
                name = "post_mid",
                type = OpenApiTypes.STR,
                location = OpenApiParameter.PATH,
                description = "Primary key (serial) of the post",
            )
        ],
        request = PostSerializer,
        responses = {
            200: OpenApiResponse(
                response = PostSerializer,
                description = "Post updated successfully"
            ),
            400: OpenApiResponse(description = "Invalid input"),
            403: OpenApiResponse(description = "Permission denied"),
            404: OpenApiResponse(description = "Post not found"),
        },
        tags = ["Post"]
    )

    post_view_delete = extend_schema(
        operation_id = "post_view_delete",
        summary = "Delete a specific post",
        description = """
            Delete a specific post by its post ID. Only the post author can delete the post..
        """,
        parameters = [
            OpenApiParameter(
                name = "author_mid",
                type = OpenApiTypes.STR,
                location = OpenApiParameter.PATH,
                description = "Primary key (serial) of the author",
            ),
            OpenApiParameter(
                name = "post_mid",
                type = OpenApiTypes.STR,
                location = OpenApiParameter.PATH,
                description = "Primary key (serial) of the post",
            )
        ],
        responses = {
            204: OpenApiResponse(description = "Post deleted successfully"),
            403: OpenApiResponse(description = "Permission denied"),
            404: OpenApiResponse(description = "Post not found"),
        },
        tags = ["Post"]
    )

    post_image_view_get = extend_schema(
        operation_id = "post_image_view_get",
        summary = "Retrieve the image of an image post",
        description = """
            Get the image inside an image post.
        """,
        parameters = [
            OpenApiParameter(
                name = "author_pk",
                type = OpenApiTypes.STR,
                location = OpenApiParameter.PATH,
                description = "Primary key (serial) of the author",
            ),
            OpenApiParameter(
                name = "post_pk",
                type = OpenApiTypes.STR,
                location = OpenApiParameter.PATH,
                description = "Primary key (serial) of the post",
            ),
            OpenApiParameter(
                name = "post_id",
                type = OpenApiTypes.STR,
                location = OpenApiParameter.PATH,
                description = "id (fqid) of the post",
            )
        ],
        responses = {
            200: OpenApiResponse(
                description = "Successfully retrieved the image",
                examples = [
                    OpenApiExample(
                        "Successful Response",
                        value = {
                            "image/png": {'an image'}
                        }
                    )
                ]
            ),
            404: OpenApiResponse(description = "Post not found"),
        },
        tags = ["PostImage"],
    )

    comments_view_get = extend_schema(
        operation_id = "comments_view_get",
        summary = "Retrieve the comments for a post",
        description = """
            Get the 'Comments' object for a single post, including the 'Comment' objects as a list
            and the count of total comments for this post. 
            The parameter provided can be:
            1: author_pk + post_pk
            2: post_id
        """,
        parameters = [
            OpenApiParameter(
                name = "author_pk",
                type = OpenApiTypes.STR,
                location = OpenApiParameter.PATH,
                description = "Primary key (serial) of the author",
            ),
            OpenApiParameter(
                name = "post_pk",
                type = OpenApiTypes.STR,
                location = OpenApiParameter.PATH,
                description = "Primary key (serial) of the post",
            ),
            OpenApiParameter(
                name = "post_id",
                type = OpenApiTypes.STR,
                location = OpenApiParameter.PATH,
                description = "id (fqid) of the post",
            )
        ],
        responses = {
            200: OpenApiResponse(
                response = CommentSerializer(many = True),
                description = "Successfully retrieved comments for the specified post",
                examples = [
                    OpenApiExample(
                        "Successful Response",
                        value = {
                            "type":"comments",
                            "page":"http://example.com/authors/1/posts/1",
                            "id":"http://example.com/api/authors/1/posts/1/comments",
                            "page_number":1,
                            "size":5,
                            "count": 10,
                            "src":['...'],
                        }
                    )
                ]
            ),
            404: OpenApiResponse(description = "Post not found"),
        },
        tags = ["Comments"],
    )

    commented_view_get = extend_schema(
        operation_id = "commented_view_get",
        summary = "Retrieve a list of comments",
        description = """
            Get a list of 'Comment' object.
            The parameter provided can be:
            1: author_pk
            2: author_id
        """,
        parameters = [
            OpenApiParameter(
                name = "author_pk",
                type = OpenApiTypes.STR,
                location = OpenApiParameter.PATH,
                description = "Primary key (serial) of the author",
            ),
            OpenApiParameter(
                name = "author_id",
                type = OpenApiTypes.STR,
                location = OpenApiParameter.PATH,
                description = "id (fqid) of the post",
            )
        ],
        responses = {
            200: OpenApiResponse(
                response = CommentSerializer,
                description = "Successfully retrieved a list of comments an author has made",
                examples = [
                    OpenApiExample(
                        "Successful Response",
                        value = [
                            {
                                "type":"comment",
                                "author": {
                                    "type": "author",
                                    "id": "http://socialapp/api/authors/abc",
                                    "display_name": "ABC",
                                    "page": "http://socialapp/authors/abc",
                                    "github": "https://github.com/abc",
                                    "profile_image": "http://socialapp/images/abc.jpg"
                                },
                                "comment": "example comment",
                                "contentType": "text/markdown",
                                "id": "http://example.com/api/authors/1/commented/1",
                                "published": "2015-03-09T13:07:04+00:00",
                                "post": "http://example.com/api/authors/1/posts/1",
                                "likes": {'...'},
                            },
                            {
                                "type":"comment",
                                "author": {
                                    "type": "author",
                                    "id": "http://socialapp/api/authors/abc",
                                    "display_name": "ABC",
                                    "page": "http://socialapp/authors/abc",
                                    "github": "https://github.com/abc",
                                    "profile_image": "http://socialapp/images/abc.jpg"
                                },
                                "comment": "example comment",
                                "contentType": "text/markdown",
                                "id": "http://example.com/api/authors/1/commented/2",
                                "published": "2015-03-10T13:07:04+00:00",
                                "post": "http://example.com/api/authors/1/posts/1",
                                "likes": {'...'},
                            }
                        ]
                    )
                ]
            ),
        },
        tags = ["Commented"]
    )

    commented_view_post = extend_schema(
        operation_id = "commented_view_post",
        summary = "Post a new comment to a post",
        description = """
            create a new comment that known which post it belongs to.
            The parameter provided is: author_pk
        """,
        parameters = [
            OpenApiParameter(
                name = "author_pk",
                type = OpenApiTypes.STR,
                location = OpenApiParameter.PATH,
                description = "Primary key (serial) of the author",
            )
        ],
        request = OpenApiRequest(
                request = AuthorSerializer,
                examples = [
                    OpenApiExample(
                        "Example Request",
                        value = {
                            "post": "http://example.com/api/authors/1/posts/1",
                            "contentType": "text/plain",
                            "comment": "test comment"
                        }
                    )
                ],
        ),
        responses = {
            201: OpenApiResponse(
                response = CommentSerializer,
                description = "Successfully post a comment",
                examples = [
                    OpenApiExample(
                        "Successful Response",
                        value = {
                            "type":"comment",
                            "author": {
                                "type": "author",
                                "id": "http://socialapp/api/authors/abc",
                                "display_name": "ABC",
                                "page": "http://socialapp/authors/abc",
                                "github": "https://github.com/abc",
                                "profile_image": "http://socialapp/images/abc.jpg"
                            },
                            "comment": "example comment",
                            "contentType": "text/markdown",
                            "id": "http://example.com/api/authors/1/commented/1",
                            "published": "2015-03-09T13:07:04+00:00",
                            "post": "http://example.com/api/authors/1/posts/1",
                            "likes": {'...'},
                        }
                    )
                ]
            ),
            400: OpenApiResponse(description = "Invalid input"),
            404: OpenApiResponse(description = "Author or Post not found"),
        },
        tags = ["Commented"]
    )

    comment_view_get = extend_schema(
        operation_id = "comment_view_get",
        summary = "Retrieve a comment",
        description = """
            Get a single 'Comment' object.
            The parameter provided can be:
            1: author_pk + post_pk + comment_id
            2: comment_id
            3: comment_id
        """,
        parameters = [
            OpenApiParameter(
                name = "author_pk",
                type = OpenApiTypes.STR,
                location = OpenApiParameter.PATH,
                description = "Primary key (serial) of the author",
            ),
            OpenApiParameter(
                name = "post_pk",
                type = OpenApiTypes.STR,
                location = OpenApiParameter.PATH,
                description = "Primary key (serial) of the post",
            ),
            OpenApiParameter(
                name = "post_id",
                type = OpenApiTypes.STR,
                location = OpenApiParameter.PATH,
                description = "id (fqid) of the post",
            )
        ],
        responses = {
            200: OpenApiResponse(
                response = CommentSerializer,
                description = "Successfully retrieved comment for a specified post",
                examples = [
                    OpenApiExample(
                        "Successful Response",
                        value = {
                                "type":"comment",
                                "author": {
                                    "type": "author",
                                    "id": "http://socialapp/api/authors/abc",
                                    "display_name": "ABC",
                                    "page": "http://socialapp/authors/abc",
                                    "github": "https://github.com/abc",
                                    "profile_image": "http://socialapp/images/abc.jpg"
                                },
                                "comment": "example comment",
                                "contentType": "text/markdown",
                                "id": "http://example.com/api/authors/1/commented/1",
                                "published": "2015-03-09T13:07:04+00:00",
                                "post": "http://example.com/api/authors/1/posts/1",
                                "likes": {'...'},
                        }
                    )
                ]
            ),
        },
        tags = ["Comment"],
    )

    likes_view_get = extend_schema(
        operation_id = "likes_view_get",
        summary = "Retrieve Likes",
        description = """
            Retrieve 'likes' object on a post, comment, or retrieve all likes that made by an author.
            The parameter provided is: 
            1: author_pk + post_pk
            2: post_id
            3: author_pk + post_pk + comment_pk
            4: author_pk
            5: author_id
        """,
        parameters = [
            OpenApiParameter(
                name = "author_pk",
                type = OpenApiTypes.STR,
                location = OpenApiParameter.PATH,
                description = "Primary key (serial) of the author",
            ),
            OpenApiParameter(
                name = "post_pk",
                type = OpenApiTypes.STR,
                location = OpenApiParameter.PATH,
                description = "Primary key (serial) of the post",
            ),
            OpenApiParameter(
                name = "post_id",
                type = OpenApiTypes.STR,
                location = OpenApiParameter.PATH,
                description = "Id (fqid) of the post",
            ),
            OpenApiParameter(
                name = "comment_pk",
                type = OpenApiTypes.STR,
                location = OpenApiParameter.PATH,
                description = "Primary key (serial) of the comment",
            ),
            OpenApiParameter(
                name = "author_id",
                type = OpenApiTypes.STR,
                location = OpenApiParameter.PATH,
                description = "Id (fqid) of the author",
            )
        ],
        responses = {
            200: OpenApiResponse(
                response = LikeSerializer(many = True),
                description = "Successfully get likes",
                examples = [
                    OpenApiExample(
                        "Successful Response",
                        value = {
                            "type":"likes",
                            "page":"http://example.com/authors/1/posts/1",
                            "id":"http://example.com/api/authors/1/posts/1/likes",
                            "page_number":1,
                            "size":50,
                            "count": 12,
                            "src":['...'],
                        }
                    )
                ]
            ),
            404: OpenApiResponse(description = "Comment or Post not found"),
        },
        tags = ["Likes"]
    )

    like_view_get = extend_schema(
        operation_id = "like_view_get",
        summary = "Retrieve Like",
        description = """
            Retrieve a single 'like' object on that made by an author.
            The parameter provided is: 
            1: like_id
            2: author_pk + like_pk
        """,
        parameters = [
            OpenApiParameter(
                name = "like_id",
                type = OpenApiTypes.STR,
                location = OpenApiParameter.PATH,
                description = "Id (fqid) of the like",
            ),
            OpenApiParameter(
                name = "author_pk",
                type = OpenApiTypes.STR,
                location = OpenApiParameter.PATH,
                description = "Primary key (serial) of the author",
            ),
            OpenApiParameter(
                name = "like_pk",
                type = OpenApiTypes.STR,
                location = OpenApiParameter.PATH,
                description = "Primary key (serial) of the like",
            )
        ],
        responses = {
            200: OpenApiResponse(
                response = LikeSerializer,
                description = "Successfully get a like",
                examples = [
                    OpenApiExample(
                        "Successful Response",
                        value = {
                            "type":"like",
                            "author": {
                                "type": "author",
                                "id": "http://socialapp/api/authors/abc",
                                "display_name": "ABC",
                                "page": "http://socialapp/authors/abc",
                                "github": "https://github.com/abc",
                                "profile_image": "http://socialapp/images/abc.jpg"
                            },
                            "published":"2015-05-09T13:07:04+00:00",
                            "id":"http://socialapp/api/authors/1/liked/1",
                            "object": "http://socialapp/authors/1/posts/1"
                        }
                    )
                ]
            ),
            404: OpenApiResponse(description = "like object not found"),
        },
        tags = ["Like"]
    )

    like_view_post = extend_schema(
        operation_id = "like_view_post",
        summary = "Post a Like",
        description = """
            Post a single 'like' object on that made by an author.
            The parameter provided is author_pk
        """,
        parameters = [
            OpenApiParameter(
                name = "author_pk",
                type = OpenApiTypes.STR,
                location = OpenApiParameter.PATH,
                description = "Primary key (serial) of the author",
            )
        ],
        request = OpenApiRequest(
                request = LikeSerializer,
                examples = [
                    OpenApiExample(
                        "Example request",
                        value = {
                            "post": "http://example.com/api/authors/1/posts/1",
                        }
                    )
                ],
        ), 
        responses = {
            201: OpenApiResponse(
                response = LikeSerializer,
                description = "Successfully post a like",
                examples = [
                    OpenApiExample(
                        "Successful Response",
                        value = {
                            "type":"like",
                            "author": {
                                "type": "author",
                                "id": "http://socialapp/api/authors/abc",
                                "display_name": "ABC",
                                "page": "http://socialapp/authors/abc",
                                "github": "https://github.com/abc",
                                "profile_image": "http://socialapp/images/abc.jpg"
                            },
                            "published":"2015-05-09T13:07:04+00:00",
                            "id":"http://socialapp/api/authors/1/liked/1",
                            "object": "http://socialapp/authors/1/posts/1"
                        }
                    )
                ]
            ),
            409: OpenApiResponse(description = "like made by the same author"),
            404: OpenApiResponse(description = "author not found"),
        },
        tags = ["Like"]
    )
