from django.contrib.auth import views as auth_views
from django.urls import path, include
from dj_rest_auth.registration.views import VerifyEmailView
from rest_framework.routers import DefaultRouter
from .views import UserProfileViewSet, CustomLoginView, CustomLogoutView, ConfirmTokenView

router = DefaultRouter()
router.register(r"", UserProfileViewSet, basename="userprofile")


urlpatterns = [
    path("", include(router.urls)),
    path("auth/login/", CustomLoginView.as_view(), name="custom-login"),
    path("auth/logout/", CustomLogoutView.as_view(), name="logout"),
    path("auth/", include("dj_rest_auth.urls")),
    path("auth/registration/", include("dj_rest_auth.registration.urls")),
    path(
        "auth/account-confirm-email/<str:key>/",
        VerifyEmailView.as_view(),
        name="account_confirm_email",
    ),
    path(
        "auth/password/reset/confirm/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path("auth/confirm-token/", ConfirmTokenView.as_view(), name="confirm-token"),
]
