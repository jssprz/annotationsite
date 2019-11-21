from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('statistics/', views.statistics, name='statistics'),
    path('tagger/', views.tagger, name='tagger'),
    path('tagger_statistics/', views.tagger_statistics, name='tagger_statistics'),
    path('tagger_summary/', views.tagger_summary, name='tagger_summary'),
    path('tagger_summary_csv/', views.tagger_summary_csv, name='tagger_summary_csv'),
    path('tweets_summary_csv/', views.tweets_summary_csv, name='tweets_summary_csv'),
    path('<str:media_id_str>/annotate/', views.annotate, name='annotate')
]
