from django.urls import path
from . import views

urlpatterns = [
    path('Home', views.Home, name='home'),
    path('Search', views.Search, name='search'),
    path('search_results/', views.search_results, name='search_results'),
    path('search_results/<str:search_query>/', views.search_results, name='search_results_with_query'),
]