from django.urls import path, include
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
    path('profile/', views.profile_view, name='profile'),
    path('posts/', views.MyPostsView, name='my-posts'),
    path('logout/', views.logout_view, name='logout'),  # Added logout route
    path('feed/', views.my_feed, name='my-feed'),
    path('follow/', views.followers_page, name='followers-page'),
]