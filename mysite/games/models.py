from django.db import models

class Game(models.Model):
    title = models.CharField(max_length=200)
    provider = models.CharField(max_length=200)
    platform = models.CharField(max_length=200)