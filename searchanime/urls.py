from django.urls import path
from . import views

urlpatterns = [
    path('', views.search_view, name='search_view'),
    path('öneri/', views.öneri_view, name='öneri_view'),
    path('autocomplete/', views.autocomplete_view, name='autocomplete'),  # Yeni URL tanımı
]