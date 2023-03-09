"""app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from .views import *


urlpatterns = [
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('analyze/', TemplateView.as_view(template_name='analyze.html'), name='analyze'),
    path('battle/', TemplateView.as_view(template_name='stockfish.html'), name='battle'),
    path('puzzle/', TemplateView.as_view(template_name='puzzle_index.html'), name='puzzle'),
    path('puzzle/opening', TemplateView.as_view(template_name='puzzle_opening.html'),
         name='opening_puzzle'),
    path('puzzle/theme', ThemeListView.as_view(),
         name='puzzle_theme'),
    path('puzzle/theme/<str:theme>/', theme_detail,
         name='theme_detail'),
    path('puzzle/<str:category>/', theme_detail_all,
         name='theme_detail_all'),
    path('opening/', opening_list,
         name='opening_all'),
    path('opening/<str:name>/', opening_detail,
         name='opening_detail'),
    path('opening/<str:name>/puzzle/', opening_detail_puzzle,
         name='opening_detail_puzzle'),
    path('opening/<str:name>/stratigy/puzzle/', opening_stratigy_puzzle,
         name='opening_stratigy_puzzle'),
]
