from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Serve the home view at the root URL
]