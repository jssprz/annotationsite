from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('statistics/', views.statistics, name='statistics'),
    path('tagger/', views.tagger, name='tagger'),
    path('demo/', views.demo, name='demo'),
    path('initialize_data_for_demo/', views.initialize_data_for_demo, name='initialize_data_for_demo'),
    path('meme_search_demo/', views.meme_search_demo, name='meme_search_demo'),
    path('tagger_statistics/', views.tagger_statistics, name='tagger_statistics'),
    path('tagger_summary/', views.tagger_summary, name='tagger_summary'),
    path('tagger_summary_csv/', views.tagger_summary_csv, name='tagger_summary_csv'),
    path('tweets_summary_csv/', views.tweets_summary_csv, name='tweets_summary_csv'),
    path('<str:media_id_str>/annotate/', views.annotate, name='annotate')
]
