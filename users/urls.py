from django.urls import path

from . import views

app_name = 'users'
urlpatterns = [
    path("registration/", views.RegistrationView.as_view(), name="registration"),  # POST
    path("login/", views.LoginView.as_view(), name="login"),  # POST

    path("profile/", views.ProfileView.as_view(), name="profile"),  # GET, PATCH

    path("profile/password/", views.ChangePasswordView.as_view(), name="change_password"),  # POST
    path('logout/', views.LogoutView.as_view(), name='logout'),  # POST
    path("profile/deactivate/", views.SoftDeactivateMeView.as_view(), name="soft_deactivate"),

]
