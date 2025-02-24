from django.urls import path, re_path
from . import views

urlpatterns = [
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