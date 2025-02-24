from django.urls import path, re_path
from . import views

urlpatterns = [
    path('api/authors/', views.AuthorsView.as_view(), name = 'api-authors'),
    
    path('api/authors/<str:author_pk>', views.AuthorView.as_view(), name = 'api-author-author_pk'),
    re_path(r'^api/authors/(?P<author_id>(http|https)://[^\/]+/?[^\/]*/api/authors/[^\/]+)$',
        views.AuthorView.as_view(),
        name = 'api-author-author_id'
    ),
    
    re_path(
        r'^api/stream/(?P<author_id>(http|https)://[^\/]+/?[^\/]*/api/authors/[^\/]+)$',
        views.StreamView.as_view(),
        name = 'api-stream-author_id'
    ),
    re_path(
        r'^api/stream/(?P<author_id>(http|https)://[^\/]+/?[^\/]*/api/authors/[^\/]+)/length$',
        views.StreamLengthView.as_view(),
        name = 'api-streamLength-author_id'
    ),
    re_path(
        r'^api/stream/(?P<author_id>(http|https)://[^\/]+/?[^\/]*/api/authors/[^\/]+)/posts/(?P<seq_num>[^\/]+)$',
        views.StreamPostView.as_view(),
        name = 'api-streamPost-author_id-seq_num'
    ),
]
