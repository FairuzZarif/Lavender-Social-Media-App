from django.contrib import admin
from authors.models import *
from follow.models import *
from posts.models import *
from comments_likes.models import *
from .models import *

admin.site.register(AuthorModel)
admin.site.register(FollowRequestModel)
admin.site.register(CommentModel)
admin.site.register(PostModel)
admin.site.register(FollowerModel)
admin.site.register(LikeModel)
admin.site.register(ShareNodeModel)
