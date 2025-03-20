from django.urls import path

from authapp.views import RegisterView, LoginView, LogoutView

app_name = "authapp"

urlpatterns = [
    path('sign-in', LoginView.as_view(), name="sign-in"),
    path('sign-up', RegisterView.as_view(), name='sign-up'),
    path('sign-out', LogoutView.as_view(), name='logout'),
]