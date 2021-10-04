# boiler plate code
from django.urls import path

# boiler plate code
from . import views

app_name = 'polls' # this is useful for template URL namespaces

"""
urlpatterns = [
    # ex: /polls/
    path('',                                      views.index,              name='index'),
    path('index_long_method/',                    views.index_long_method,  name='index_long_method'),
    path('index1/',                               views.index1,             name='index1'),
    # ex: /polls/5/
    path('<int:question_id>/',                    views.detail,             name='detail'),
    path('detail_long_method/<int:question_id>/', views.detail_long_method, name='detail_long_method'),
    # ex: /polls/5/results/
    path('<int:question_id>/results/',            views.results,            name='results'),
    # ex: /polls/5/vote/
    path('<int:question_id>/vote/',               views.vote,               name='vote'),
]
"""

# shortcut method
urlpatterns = [
    path('',                        views.IndexView.as_view(),   name='index'),
    path('<int:pk>/',               views.DetailView.as_view(),  name='detail'),
    path('<int:pk>/results/',       views.ResultsView.as_view(), name='results'),
    path('<int:question_id>/vote/', views.vote,                  name='vote'),
]
