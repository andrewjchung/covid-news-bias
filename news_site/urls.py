"""Defines URL patterns for news_site."""

from django.urls import path
from . import views

app_name = 'news_site'
urlpatterns = [
    #Home Page 
    path("", views.index, name='index'),

    #Search result
    path("results/", views.results, name="results"),
]