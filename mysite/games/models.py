from django.db import models


class Game(models.Model):
    title = models.CharField(max_length=200)
    provider = models.CharField(max_length=200)
    platform = models.CharField(max_length=200)
    type = models.CharField(max_length=50, null=True)
    year = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return str(self.id) + " - " + self.title + " - " + self.platform + " - " + self.provider


class Settings(models.Model):
    sort_by = models.CharField(max_length=200, default="title")
    show_id = models.BooleanField(default=True)
    show_title = models.BooleanField(default=True)
    show_provider = models.BooleanField(default=True)
    show_platform = models.BooleanField(default=True)
    show_type = models.BooleanField(default=True)
    show_year = models.BooleanField(default=True)


class FieldVisibleAlways(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
