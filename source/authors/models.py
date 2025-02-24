from django.db import models

class AuthorModel(models.Model):
    
    username = models.CharField(primary_key = True, max_length = 512)
    password = models.CharField(max_length = 512)
    lastGithubUpdate = models.DateTimeField(auto_now_add = True)
    isVerified = models.BooleanField(default = False)
    type = models.CharField(max_length = 64, default = "author")
    id = models.CharField(unique = True, max_length = 1024)
    host = models.CharField(max_length = 1024, blank = True)
    displayName = models.CharField(max_length = 512, blank = True)
    github = models.CharField(max_length = 1024, blank = True)
    profileImage = models.CharField(max_length = 1024, blank = True)
    page = models.CharField(max_length = 1024, blank = True)

    def is_authenticated(self):
        return True