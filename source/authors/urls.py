from django.urls import path
from . import views

urlpatterns = [
    path('authors/', views.AuthorListView.as_view(), name='author-list'),
    path('authors/<int:author_id>/', views.AuthorDetailView.as_view(), name='author-detail'),
    path('authors/<int:author_id>/inbox', views.AuthorInboxView.as_view(), name='author-inbox'),
]