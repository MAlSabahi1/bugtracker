from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from django.utils.translation import gettext_lazy as _

from .models import User, System, Screen, Issue, Comment, IssueLog


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("username", "email", "role", "get_groups", "is_active")
    list_filter = ("role", "groups", "is_active")
    fieldsets = BaseUserAdmin.fieldsets + (
        (_("Rasid System Info"), {"fields": ("role",)}),
    )

    def get_groups(self, obj):
        return ", ".join([g.name for g in obj.groups.all()])
    get_groups.short_description = "Groups"


@admin.register(System)
class SystemAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "get_groups")
    list_filter = ("is_active", "groups")
    search_fields = ("name",)

    def get_groups(self, obj):
        return ", ".join([g.name for g in obj.groups.all()])
    get_groups.short_description = "Assigned Groups"


@admin.register(Screen)
class ScreenAdmin(admin.ModelAdmin):
    list_display = ("name", "system", "get_groups")
    list_filter = ("system", "groups")
    search_fields = ("name",)

    def get_groups(self, obj):
        return ", ".join([g.name for g in obj.groups.all()])
    get_groups.short_description = "Assigned Groups"


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    readonly_fields = ("user", "created_at")


class IssueLogInline(admin.TabularInline):
    model = IssueLog
    extra = 0
    readonly_fields = ("action", "old_value", "new_value", "changed_by", "created_at")


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = ("title", "system", "issue_type", "priority", "status", "reported_by", "assigned_to", "created_at")
    list_filter = ("status", "priority", "issue_type", "system")
    search_fields = ("title", "description")
    inlines = [CommentInline, IssueLogInline]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("issue", "user", "created_at")
    list_filter = ("created_at",)


@admin.register(IssueLog)
class IssueLogAdmin(admin.ModelAdmin):
    list_display = ("issue", "action", "changed_by", "created_at")
    list_filter = ("action", "created_at")
