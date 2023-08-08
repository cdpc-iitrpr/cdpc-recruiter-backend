from django.urls import path
from .views import signup, signin, verify, logout

# Define all the URL patterns here
urlpatterns = [
    path('signup/', signup),
    path('login/', signin),
    path('verify/', verify),
    path('logout/', logout)
]