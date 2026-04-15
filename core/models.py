from django.db import models
from django.contrib.auth.models import AbstractUser, Group
from django.utils.translation import gettext_lazy as _


# ──────────────────────────────────────────────
# System
# ──────────────────────────────────────────────
class System(models.Model):
    name = models.CharField(_("Name"), max_length=255)
    description = models.TextField(_("Description"), null=True, blank=True)
    is_active = models.BooleanField(_("Is Active"), default=True)
    groups = models.ManyToManyField(
        Group,
        related_name="systems",
        verbose_name=_("Groups"),
        blank=True,
        help_text=_("Groups that have access to this system.")
    )

    class Meta:
        verbose_name = _("System")
        verbose_name_plural = _("Systems")
        ordering = ["name"]

    def __str__(self):
        return self.name


# ──────────────────────────────────────────────
# Screen
# ──────────────────────────────────────────────
class Screen(models.Model):
    system = models.ForeignKey(
        System,
        on_delete=models.CASCADE,
        related_name="screens",
        verbose_name=_("System"),
    )
    name = models.CharField(_("Name"), max_length=255)
    groups = models.ManyToManyField(
        Group,
        related_name="screens",
        verbose_name=_("Groups"),
        blank=True,
        help_text=_("Groups that have access to this specific screen.")
    )

    class Meta:
        verbose_name = _("Screen")
        verbose_name_plural = _("Screens")
        ordering = ["system", "name"]

    def __str__(self):
        return f"{self.system.name} → {self.name}"


# ──────────────────────────────────────────────
# Custom User
# ──────────────────────────────────────────────
class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN    = "admin",    _("Admin")
        FRONTEND = "frontend", _("FrontEnd")
        BACKEND  = "backend",  _("BackEnd")

    role = models.CharField(
        _("Role"),
        max_length=20,
        choices=Role.choices,
        default=Role.FRONTEND,
    )

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        ordering = ["username"]

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN or self.is_superuser

    @property
    def is_frontend(self):
        return self.role == self.Role.FRONTEND

    @property
    def is_backend(self):
        return self.role == self.Role.BACKEND


# ──────────────────────────────────────────────
# Issue
# ──────────────────────────────────────────────
class Issue(models.Model):
    class IssueType(models.TextChoices):
        BUG = "bug", _("Bug")
        SECURITY = "security", _("Security")
        UI = "ui", _("UI")

    class Priority(models.TextChoices):
        LOW = "low", _("Low")
        MEDIUM = "medium", _("Medium")
        HIGH = "high", _("High")
        CRITICAL = "critical", _("Critical")

    class Status(models.TextChoices):
        OPEN = "open", _("Open")
        IN_PROGRESS = "in_progress", _("In Progress")
        RESOLVED = "resolved", _("Resolved")
        CLOSED = "closed", _("Closed")
        REOPENED = "reopened", _("Reopened")

    class TargetTeam(models.TextChoices):
        FRONTEND = "frontend", _("FrontEnd")
        BACKEND  = "backend",  _("BackEnd")

    class Resolution(models.TextChoices):
        FIXED = "fixed", _("Fixed")
        DUPLICATE = "duplicate", _("Duplicate")
        WONT_FIX = "wont_fix", _("Won't Fix")
        WORKS_FOR_ME = "works_for_me", _("Works For Me")
        NOT_A_BUG = "not_a_bug", _("Not a Bug")
        UNRESOLVED = "unresolved", _("Unresolved")

    title = models.CharField(_("Title"), max_length=255)
    description = models.TextField(_("Description"))

    system = models.ForeignKey(
        System,
        on_delete=models.CASCADE,
        related_name="issues",
        verbose_name=_("System"),
    )
    screen = models.ForeignKey(
        Screen,
        on_delete=models.CASCADE,
        related_name="issues",
        verbose_name=_("Screen"),
    )

    reported_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reported_issues",
        verbose_name=_("Reported By"),
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_issues",
        verbose_name=_("Assigned To"),
    )

    issue_type = models.CharField(
        _("Issue Type"),
        max_length=20,
        choices=IssueType.choices,
    )
    priority = models.CharField(
        _("Priority"),
        max_length=20,
        choices=Priority.choices,
        default=Priority.MEDIUM,
    )
    status = models.CharField(
        _("Status"),
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN,
    )

    target_team = models.CharField(
        _("Target Team"),
        max_length=20,
        choices=TargetTeam.choices,
        default=TargetTeam.FRONTEND,
    )

    steps_to_reproduce = models.TextField(_("Steps to Reproduce"), null=True, blank=True)
    expected_result = models.TextField(_("Expected Result"), null=True, blank=True)
    actual_result = models.TextField(_("Actual Result"), null=True, blank=True)

    resolution = models.CharField(
        _("Resolution"),
        max_length=20,
        choices=Resolution.choices,
        default=Resolution.UNRESOLVED,
    )
    root_cause = models.TextField(_("Root Cause"), null=True, blank=True)

    image = models.ImageField(
        _("Image Attachment"),
        upload_to="issues/images/",
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)

    class Meta:
        verbose_name = _("Issue")
        verbose_name_plural = _("Issues")
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.get_priority_display()}] {self.title}"


# ──────────────────────────────────────────────
# Comment
# ──────────────────────────────────────────────
class Comment(models.Model):
    issue = models.ForeignKey(
        Issue,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name=_("Issue"),
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name=_("User"),
    )
    content = models.TextField(_("Comment Content"))

    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)

    class Meta:
        verbose_name = _("Comment")
        verbose_name_plural = _("Comments")
        ordering = ["created_at"]

    def __str__(self):
        return f"Comment by {self.user.username} on #{self.issue.pk}"


# ──────────────────────────────────────────────
# Issue Log (Audit Trail)
# ──────────────────────────────────────────────
class IssueLog(models.Model):
    issue = models.ForeignKey(
        Issue,
        on_delete=models.CASCADE,
        related_name="logs",
        verbose_name=_("Issue"),
    )
    action = models.CharField(_("Action"), max_length=255)
    old_value = models.TextField(_("Old Value"), null=True, blank=True)
    new_value = models.TextField(_("New Value"), null=True, blank=True)
    changed_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="issue_logs",
        verbose_name=_("Changed By"),
    )

    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)

    class Meta:
        verbose_name = _("Issue Log")
        verbose_name_plural = _("Issue Logs")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.action} — Issue #{self.issue.pk} by {self.changed_by.username}"


# ──────────────────────────────────────────────
# Notification
# ──────────────────────────────────────────────
class Notification(models.Model):
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name=_("Recipient")
    )
    issue = models.ForeignKey(
        Issue,
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name=_("Issue")
    )
    message = models.CharField(_("Message"), max_length=255)
    is_read = models.BooleanField(_("Is Read"), default=False)
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)

    class Meta:
        verbose_name = _("Notification")
        verbose_name_plural = _("Notifications")
        ordering = ["-created_at"]

    def __str__(self):
        return f"Notification for {self.recipient.username}: {self.message}"
