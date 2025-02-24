from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from posts.models import PostModel as Post
from authors.models import AuthorModel as Author
import json
import uuid
from .schema_defs import *

def HomeView(request):
    return render(request, 'home.html')

def LoginView(request):
    return render(request, 'login.html')

def profile_view(request):
    return render(request, 'profile.html')

def MyPostsView(request):
    try:
        # Assuming `displayName` in Author corresponds to `username` of the logged-in user
        author = Author.objects.get(displayName=request.user.username)
    except Author.DoesNotExist:
        # Return an empty list if no corresponding Author is found
        return render(request, 'my_posts.html', {'posts': []})

    # Fetch all posts by this author
    user_posts = Post.objects.filter(author=author).order_by('-published')

    context = {
        'posts': user_posts,
    }
    return render(request, 'my_posts.html', context)

def logout_view(request):
    logout(request)  # Logs out the user
    return redirect('login')  # Redirects to the login page

def my_feed(request):
    # Fetch all posts as feed (replace this with filtered logic later)
    feed_posts = Post.objects.all().order_by('-published')  # Add your logic here
    return render(request, 'my_feed.html', {'feed_posts': feed_posts})

def followers_page(request):
    # Simulating dummy authors and followers for now
    current_author = Author.objects.filter(displayName=request.user.username).first()
    
    if not current_author:
        return render(request, 'follow_page.html', {'followed_users': [], 'followers': []})
    
    # Replace these dummy lists with actual queries
    followed_users = Author.objects.exclude(displayName=current_author.displayName)[:5]  # Dummy data
    followers = Author.objects.exclude(displayName=current_author.displayName).order_by('-displayName')[:5]  # Dummy data

    context = {
        'followed_users': followed_users,
        'followers': followers,
    }

    return render(request, 'follow_page.html', context)
