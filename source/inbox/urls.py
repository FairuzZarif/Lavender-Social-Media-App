from django.urls import path, re_path
from . import views

urlpatterns = [
    path('api/authors/<str:author_pk>/inbox', views.InboxView.as_view(), name = 'api-inbox-author_pk'),
]
