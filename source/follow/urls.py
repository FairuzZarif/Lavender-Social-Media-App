from django.urls import path
from . import views

urlpatterns = [
    path('authors/<int:author_id>/follow/<int:target_author_id>/', views.FollowAuthorView.as_view(), name='follow-author'),
]
