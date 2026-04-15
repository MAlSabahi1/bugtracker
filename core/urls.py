from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path("login/", views.UserLoginView.as_view(), name="login"),
    path("logout/", views.UserLogoutView.as_view(), name="logout"),

    # Dashboard
    path("", views.DashboardView.as_view(), name="index"),
    path("dashboard/", views.DashboardView.as_view(), name="dashboard"),

    # Issues
    path("issues/", views.IssueListView.as_view(), name="issue-list"),
    path("issues/create/", views.IssueCreateView.as_view(), name="issue-create"),
    path("issues/<int:pk>/", views.IssueDetailView.as_view(), name="issue-detail"),
    path("issues/<int:pk>/edit/", views.IssueUpdateView.as_view(), name="issue-update"),
    path("issues/<int:pk>/delete/", views.IssueDeleteView.as_view(), name="issue-delete"),

    # Comments
    path("issues/<int:issue_pk>/comment/", views.CommentCreateView.as_view(), name="comment-create"),

    # Systems
    path("systems/", views.SystemListView.as_view(), name="system-list"),
    path("systems/create/", views.SystemCreateView.as_view(), name="system-create"),
    path("systems/<int:pk>/edit/", views.SystemUpdateView.as_view(), name="system-update"),
    path("systems/<int:pk>/delete/", views.SystemDeleteView.as_view(), name="system-delete"),

    # Groups (Django Auth Groups)
    path("groups/", views.GroupListView.as_view(), name="group-list"),
    path("groups/create/", views.GroupCreateView.as_view(), name="group-create"),
    path("groups/<int:pk>/edit/", views.GroupUpdateView.as_view(), name="group-update"),
    path("groups/<int:pk>/delete/", views.GroupDeleteView.as_view(), name="group-delete"),

    # Screens
    path("screens/", views.ScreenListView.as_view(), name="screen-list"),
    path("screens/create/", views.ScreenCreateView.as_view(), name="screen-create"),
    path("screens/<int:pk>/edit/", views.ScreenUpdateView.as_view(), name="screen-update"),
    path("screens/<int:pk>/delete/", views.ScreenDeleteView.as_view(), name="screen-delete"),

    # Users
    path("users/", views.UserListView.as_view(), name="user-list"),
    path("users/create/", views.UserCreateView.as_view(), name="user-create"),
    path("users/<int:pk>/edit/", views.UserUpdateView.as_view(), name="user-update"),
    path("users/<int:pk>/delete/", views.UserDeleteView.as_view(), name="user-delete"),

    # AJAX
    path("ajax/load-screens/", views.load_screens, name="ajax-load-screens"),
    path("ajax/issues/<int:pk>/status/", views.update_issue_status, name="ajax-update-status"),

    # Notifications
    path("notifications/<int:pk>/read/", views.mark_notification_read, name="mark-notification-read"),
]
