from django.urls import path

from core.views_rbac import (RBACElementListView, RBACRoleListView,
                             RBACRuleDetailView, RBACRuleListCreateView)

app_name = "rbac"

urlpatterns = [
    path("roles/", RBACRoleListView.as_view(), name="rbac_roles"),
    path("elements/", RBACElementListView.as_view(), name="rbac_elements"),
    path("rules/", RBACRuleListCreateView.as_view(), name="rbac_rules"),
    path("rules/<int:pk>/", RBACRuleDetailView.as_view(), name="rbac_rule_detail"),
]
