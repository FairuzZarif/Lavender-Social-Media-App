from django.urls import path, include, re_path
from . import views
from django.shortcuts import redirect

urlpatterns = [   
    path(
        'api/authors/<str:author_pk>/posts/<str:post_pk>/comments',
        views.CommentsView.as_view(),
        name = 'api-comments-author_pk-post_pk'
    ),
    re_path(
        r'^api/posts/(?P<post_id>(http|https)://[^\/]+/?[^\/]*/api/authors/[^\/]+/posts/[^\/]+)/comments$',
        views.CommentsView.as_view(),
        name = 'api-comments-post_id'
    ),
    path(
        'api/authors/<str:author_pk>/commented',
        views.CommentedView.as_view(),
        name = 'api-commented-author_pk'
    ),
    re_path(
        r'^api/authors/(?P<author_id>(http|https)://[^\/]+/?[^\/]*/api/authors/[^\/]+)/commented$',
        views.CommentedView.as_view(),
        name = 'api-commented-author_id'
    ),
    re_path(
        r'^api/authors/(?P<author_pk>[^\/]+)/post/(?P<post_pk>[^\/]+)/comment/(?P<comment_id>(http|https)://[^\/]+/api/authors/[^\/]+/commented/[^\/]+)$',
        views.CommentView.as_view(),
        name = 'api-comment-author_pk-post_pk-comment_id'
    ),
    re_path(
        r'^api/authors/(?P<author_pk>[^\/]+)/commented/(?P<comment_pk>[^\/]+)$',
        views.CommentView.as_view(),
        name = 'api-comment-comment_id'
    ),
    re_path(
        r'^api/commented/(?P<comment_id>(http|https)://[^\/]+/api/authors/[^\/]+/commented/[^\/]+)$',
        views.CommentView.as_view(),
        name = 'api-commented-comment_id'
    ),


    path(
        'api/authors/<str:author_pk>/posts/<str:post_pk>/likes',
        views.LikesView.as_view(),
        name = 'api-postLikes-author_pk-post_pk'
    ),
    re_path(
        r'^api/authors/(?P<author_id>(http|https)://[^\/]+/?[^\/]*/api/authors/[^\/]+)/liked$',
        views.LikesView.as_view(),
        name = 'api-authorLikes-author_id'
    ),
    re_path(
        r'^api/posts/(?P<post_id>(http|https)://[^\/]+/?[^\/]*/api/authors/[^\/]+/posts/[^\/]+)/likes$',
        views.LikesView.as_view(),
        name = 'api-postLikes-post_id'
    ),
    re_path(
        r'^api/authors/(?P<author_pk>[^\/]+)/posts/(?P<post_pk>[^\/]+)/comments/(?P<comment_id>(http|https)://[^\/]+/api/authors/[^\/]+/commented/[^\/]+)/likes$',
        views.LikesView.as_view(),
        name = 'api-commentLikes-author_pk-post_pk-comment_id'
    ),
    path(
        'api/authors/<str:author_pk>/liked',
        views.LikesView.as_view(), 
        name = 'api-authorLikes-author_pk'
    ),
    path(
        'api/authors/<str:author_pk>/liked/send/',
        views.LikeView.as_view(), 
        name = 'api-sendLike-author_pk'
    ),
    re_path(
        r'^api/liked/(?P<like_id>(http|https).+)$',
        views.LikeView.as_view(), 
        name = 'api-like-like_id'
    ),
    path(
        'api/authors/<str:author_pk>/liked/<str:like_pk>',
        views.LikeView.as_view(),
        name = 'api-like-author_pk-like_pk'
    ),
]