from django.db import models
from .tools import *

class ShareNodeModel(models.Model):
    host = models.CharField(primary_key = True, max_length = 1024)
    allowIn = models.BooleanField(default = False)
    inUsername = models.CharField(max_length = 512)
    inPassword = models.CharField(max_length = 512, default = generate_password)
    allowOut = models.BooleanField(default = False)
    outUsername = models.CharField(max_length = 512)
    outPassword = models.CharField(max_length = 512)