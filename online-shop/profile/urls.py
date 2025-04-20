from profile.views import ProfileView, UpdateAvatarView, UpdatePasswordView

from django.urls import path

app_name = "profile"

urlpatterns = [
    path("profile/", ProfileView.as_view(), name="profile"),
    path("profile/avatar/", UpdateAvatarView.as_view(), name="update-avatar"),
    path("profile/password/", UpdatePasswordView.as_view(), name="update-password"),
]
