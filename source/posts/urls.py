from django.urls import path, re_path
from . import views

urlpatterns = [
    path(
        'api/authors/<str:author_pk>/posts/',
        views.PostsView.as_view(),
        name = 'api-posts-author_pk'
    ),
    path(
        'api/authors/<str:author_pk>/posts/<str:post_pk>',
        views.PostView.as_view(),
        name = 'api-post-author_pk-post_pk'
    ),
    re_path(
        r'^api/posts/(?P<post_id>(http|https)://[^\/]+/?[^\/]*/api/authors/[^\/]+/posts/[^\/]+)$',
        views.PostView.as_view(),
        name = 'api-post-post_id'
    ),
    path(
        'api/authors/<str:author_pk>/posts/<str:post_pk>/image',
        views.PostImageView.as_view(),
        name = 'api-postImage-author_pk-post_pk'
    ),
    re_path(
        r'^api/posts/(?P<post_id>(http|https)://[^\/]+/?[^\/]*/api/authors/[^\/]+/posts/[^\/]+)/image$',
        views.PostImageView.as_view(),
        name = 'api-postImage-post_id'
    ),
    
    path('api/profileimage/<str:img_id>', views.profileImageView.as_view(), name = 'api-profileimage-img_id'),
]
