from django.urls import path

from users.views_admin import AdminUserDetailView, AdminUserListCreateView

app_name = "users_admin"

urlpatterns = [
    path("users/", AdminUserListCreateView.as_view(), name="admin_user_list_create"),
    path("users/<int:pk>/", AdminUserDetailView.as_view(), name="admin_user_detail"),
]