from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('statistics', views.statistics, name='statistics'),
    path('tagger', views.tagger, name='tagger')
]
