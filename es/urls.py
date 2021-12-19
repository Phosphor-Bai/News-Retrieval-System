from django.urls import path
from . import views

app_name = 'es'
urlpatterns = [
    path('', views.index, name='index'),
    path('results/', views.search_results, name='results'),
]