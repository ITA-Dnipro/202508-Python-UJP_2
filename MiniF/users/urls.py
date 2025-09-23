from django.urls import path, include
from dj_rest_auth.registration.views import VerifyEmailView
from .views import CustomLoginView

urlpatterns = [
    path("auth/login/", CustomLoginView.as_view(), name="custom-login"),
    path("auth/", include("dj_rest_auth.urls")),
    path("auth/registration/", include("dj_rest_auth.registration.urls")),
    path(
        "auth/account-confirm-email/<str:key>/",
        VerifyEmailView.as_view(),
        name="account_confirm_email",
    ),
]
