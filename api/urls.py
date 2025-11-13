from django.urls import path, include
from .views import (
    CreateCustomUserApiView,
    ListCreateTemplateApiView,
    TemplateDetailApiView,
    ListCreateCategoryApiView,
    CategoryDetailApiView,
    ListCreateJournalEntryApiView,
    JournalEntryDetailApiView,
    ListCreateTemplateFieldApiView,
    TemplateFieldDetailApiView,
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
    path(
        "templates/<uuid:uuid>/",
        TemplateDetailApiView.as_view(),
        name="template-detail",
    ),
    path("categories/", ListCreateCategoryApiView.as_view(), name="category-list"),
    path(
        "categories/<uuid:uuid>/",
        CategoryDetailApiView.as_view(),
        name="category-detail",
    ),
    path(
        "template-fields/",
        ListCreateTemplateFieldApiView.as_view(),
        name="templatefield-list",
    ),
    path(
        "template-fields/<int:id>/",
        TemplateFieldDetailApiView.as_view(),
        name="templatefield-detail",
    ),
    path(
        "journal-entries/",
        ListCreateJournalEntryApiView.as_view(),
        name="journalentry-list",
    ),
    path(
        "journal-entries/<uuid:uuid>/",
        JournalEntryDetailApiView.as_view(),
        name="journalentry-detail",
    ),
]
