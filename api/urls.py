from django.urls import path
from .views import *
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


# Define all the URL patterns here
urlpatterns = [
    path('signup/', signup),
    path('login/', signin),
    path('verify/', verify),
    path('signout/', signout),

    path('recruiterJAF/',RecruiterJAF),
    path('recruiterJAF/<int:form_id>',RecruiterJAF),
    path('recruiterSubmitJAF/',RecruiterSubmitJAF),
    path('recruiterSubmitJAF/<int:form_id>',RecruiterSubmitJAF),

    path('recruiterINF/',RecruiterINF),
    path('recruiterINF/<int:form_id>',RecruiterINF),
    path('recruiterSubmitINF/',RecruiterSubmitINF),
    path('recruiterSubmitINF/<int:form_id>',RecruiterSubmitINF),

    path('spocJAF/',SpocJAF),
    path('spocJAF/<int:form_id>',SpocJAF),
    path('spocINF/',SpocINF),
    path('spocINF/<int:form_id>',SpocINF),  

    path('spocDetails/',SpocDetails),
    path('departmentPrograms/<str:degree>',DepartmentPrograms),

    path('jdFileUpload/<int:form_id>/',JDFileUpload),
    path('jdFileDownload/<int:form_id>/',JDFileDownload),

    # make the path for token refresh
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]