from django.urls import path, include
from .views import (
    CreateCustomUserApiView,
    UserProfileApiView,
    ListCompaniesApiView,
    CompanyViewSet,
    get_companies
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'company', CompanyViewSet, basename='company')

urlpatterns = [
    path("register", CreateCustomUserApiView.as_view(), name="signup"),
    path("login", TokenObtainPairView.as_view(), name="signin"),
    path("refresh", TokenRefreshView.as_view(), name="refresh"),
    path("profile", UserProfileApiView.as_view(), name="profile"),
    path("companies", ListCompaniesApiView.as_view(), name="companies"),
    path("get_companies", get_companies, name="get_companies"),
    path("", include(router.urls)), # Add this line
]
