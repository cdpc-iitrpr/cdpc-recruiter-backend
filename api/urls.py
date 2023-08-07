from django.urls import path
from .views import signup

# Define all the URL patterns here
urlpatterns = [
    path('signup/', signup)
]