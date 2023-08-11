from django.urls import path
from .views import *

# Define all the URL patterns here
urlpatterns = [
    path('signup/', signup),
    path('login/', signin),
    path('verify/', verify),
    path('logout/', logout),
    path('signout/', signout),

    path('recruiterJAF/',RecruiterJAF),
    path('recruiterJAF/<int:form_id>',RecruiterJAF),
    path('recruiterSubmitJAF/',RecruiterSubmitJAF),
    path('recruiterSubmitJAF/<int:form_id>',RecruiterSubmitJAF),

    path('recruiterINF/',RecruiterINF),
    path('recruiterSubmitINF/<int:form_id>',RecruiterSubmitINF),

    path('spocDetails/',SpocDetails),
    path('departmentPrograms/<str:degree>',DepartmentPrograms),
]