from django.urls import include, path

urlpatterns = [

    path('api/users/', include('users.urls', namespace='users')),
    path("api/admin/", include("users.urls_admin", namespace="users_admin")),
    path("api/rbac/", include("core.urls_rbac", namespace="rbac")),

]
