from django.urls import path, include
from dj_rest_auth.registration.views import VerifyEmailView
from .views import CustomLoginView, CustomLogoutView
from django.contrib.auth import views as auth_views

urlpatterns = [
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
]
