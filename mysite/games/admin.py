from django.contrib import admin

# Register your models here.

from .models import FieldVisibleAlways, Game, Settings 

admin.site.register(FieldVisibleAlways)
admin.site.register(Game)
admin.site.register(Settings)
