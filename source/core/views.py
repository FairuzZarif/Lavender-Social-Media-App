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


def author(request, author_id):
    return render(request, 'author.html')

def author_followers(request, author_id):
    return render(request, 'followers.html')

def author_following(request, author_id):
    return render(request, 'following.html')

def author_edit(request):
    return render(request, 'author_edit.html')

def post(request, post_id):
    return render(request, "post_detail.html", {'post_url': post_id})
