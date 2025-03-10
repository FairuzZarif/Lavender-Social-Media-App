from django.urls import path, re_path
from . import views

urlpatterns = [
    path(
        'api/authors/<str:actor_pk>/following',
        views.FollowingView.as_view(),
        name = 'api-following-author_pk'
    ),
    path(
        'api/authors/<str:object_pk>/followers',
        views.FollowersView.as_view(),
        name = 'api-follwers-author_pk'
    ),
    re_path(
        r'^api/authors/(?P<actor_pk>[^\/]+)/fre/(?P<object_id>(http|https).+)$',
        views.FollowerRemoteView.as_view(),
        name = 'api-remote-follower-actor_pk-object_id'
    ),
    re_path(
        r'^api/authors/(?P<object_pk>[^\/]+)/followers/(?P<actor_id>(http|https).+)$',
        views.FollowerView.as_view(),
        name = 'api-follower-object_pk-actor_id'
    ),
    path(
        'api/authors/<str:object_pk>/froe/',
        views.FollowRequestsObjectEnd.as_view(),
        name = 'api-getFollow-object_pk'
    ),
    re_path(
        r'^api/authors/(?P<object_pk>[^\/]+)/froe/(?P<actor_id>(http|https).+)$',
        views.FollowRequestObjectEnd.as_view(),
        name = 'api-handleFollow-object_pk-actor_id'
    ),
    re_path(
        r'^api/authors/(?P<actor_pk>[^\/]+)/frae/(?P<object_id>(http|https).+)$',
        views.FollowRequestActorEnd.as_view(),
        name = 'api-handleFollow-actor_pk-object_id'
    ),

]
