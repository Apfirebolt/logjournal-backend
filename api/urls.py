from django.urls import path, include
from .views import (
    CreateCustomUserApiView,
    ListCreateTemplateApiView,
    TemplateDetailApiView
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path("register", CreateCustomUserApiView.as_view(), name="signup"),
    path("login", TokenObtainPairView.as_view(), name="signin"),
    path("refresh", TokenRefreshView.as_view(), name="refresh"),
    path("templates/", ListCreateTemplateApiView.as_view(), name="template-list"),
    path("templates/<uuid:uuid>/", TemplateDetailApiView.as_view(), name="template-detail"),
]
