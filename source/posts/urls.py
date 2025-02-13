from django.urls import path
from . import views

urlpatterns = [
    path('authors/<int:author_id>/posts/', views.PostListView.as_view(), name='author-posts'),
    path('authors/<int:author_id>/posts/<int:post_id>/', views.PostDetailView.as_view(), name='post-detail'),
    path('authors/<int:author_id>/posts/<int:post_id>/comments/', views.CommentListView.as_view(), name='post-comments'),
]
