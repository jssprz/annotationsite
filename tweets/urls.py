from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('statistics/', views.statistics, name='statistics'),
    path('tagger/', views.tagger, name='tagger'),
    path('tagger_statistics/', views.tagger_statistics, name='tagger_statistics'),
    path('<str:media_id_str>/annotate/', views.annotate, name='annotate')
]
