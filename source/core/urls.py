from django.urls import path, include, re_path
from . import views
from django.shortcuts import redirect

app_name = "socialapp"
urlpatterns = [
    path('', lambda request: redirect('socialapp:login')),
    path('', include("authors.urls"),),
    path('', include("follow.urls")),
    path('', include("posts.urls")),
    path('', include("comments_likes.urls")),
    path('', include("inbox.urls")),

    path('login/', views.LoginView, name='login'),

    path('home/', views.HomeView, name='home'),
     
    re_path(
        r'^authors/(?P<author_id>(http|https)://[^\/]+/?[^\/]*/api/authors/[^\/]+)$',
        views.author,
        name = 'author'
    ),
    path(
        'authors/my/edit',
        views.author_edit,
        name = 'author-edit'
    ),
    re_path(
        r'authors/(?P<author_id>(http|https)://[^\/]+/?[^\/]*/api/authors/[^\/]+)/followers$',
        views.author_followers,
        name = 'author-followers'
    ),
    re_path(
        r'authors/(?P<author_id>(http|https)://[^\/]+/?[^\/]*/api/authors/[^\/]+)/following$',
        views.author_following,
        name = 'author-following'
    ),
    path(
        'posts/<path:post_id>',
        views.post,
        name = 'post'
    ),
]
