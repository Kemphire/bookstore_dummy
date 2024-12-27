# This is no longer used, since we migrated to allauth
from django.urls import path

from .views import SignupPageView


urlpatterns = [
    path("signup/", SignupPageView.as_view(), name="signup"),
]
