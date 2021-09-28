# boiler plate code
from django.urls import path

# boiler plate code
from . import views

app_name = 'games' # this is useful for template URL namespaces

urlpatterns = [
    # ex: /games/
    path('',              views.index,  name='index'),
    path('submit',        views.submit, name='submit'),
    path('<int:game_id>', views.detail, name='detail'),
]