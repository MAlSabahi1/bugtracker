from django.views.generic import TemplateView, ListView, CreateView, DetailView, UpdateView, DeleteView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import Group
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.db.models import Q, Count, FloatField, ExpressionWrapper
from django.db.models.functions import TruncMonth
from django.utils import timezone
import datetime
import json
import calendar
from django.utils.translation import gettext_lazy as _
from django.utils.formats import date_format
from django.contrib.auth.decorators import login_required

from web_project import TemplateLayout
from web_project.template_helpers.theme import TemplateHelper

from .models import Issue, Comment, IssueLog, System, Screen, User, Notification
from .forms import (
    LoginForm,
    IssueForm,
    IssueFilterForm,
    CommentForm,
    SystemForm,
    ScreenForm,
    GroupForm,
    UserForm,
    ReportFilterForm,
    UserProfileForm,
)


# ──────────────────────────────────────────────
# Auth Views
# ──────────────────────────────────────────────
class AdminRequiredMixin(LoginRequiredMixin):
    """Restrict view to admin users only. Redirects others to dashboard."""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.is_admin:
            return redirect("dashboard")
        return super().dispatch(request, *args, **kwargs)


class UserLoginView(LoginView):
    template_name = "core/auth/login.html"
    form_class = LoginForm

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        context.update(
            {"layout_path": TemplateHelper.set_layout("layout_blank.html", context)}
        )
        return context


class UserLogoutView(LogoutView):
    next_page = reverse_lazy("login")


# ──────────────────────────────────────────────
# Dashboard
# ──────────────────────────────────────────────
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "core/dashboard.html"

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        user = self.request.user

        # ── FrontEnd / BackEnd: limited dashboard ──
        if not user.is_admin:
            team = user.role  # 'frontend' or 'backend'
            user_systems = System.objects.filter(groups__user=user).distinct()
            
            # Base filter by team role
            my_issues = Issue.objects.filter(target_team=team)
            
            # Additional restriction ONLY if user belongs to system groups
            if user_systems.exists():
                my_issues = my_issues.filter(system__in=user_systems)
                
            context["my_issues_count"]   = my_issues.count()
            context["open_issues"]        = my_issues.filter(status="open").count()
            context["in_progress_issues"] = my_issues.filter(status="in_progress").count()
            context["resolved_issues"]    = my_issues.filter(status="resolved").count()
            context["recent_issues"]      = my_issues.select_related(
                "system", "reported_by"
            ).order_by("-created_at")[:10]
            # Use annotated systems for the cards
            systems_qs = user_systems if user_systems.exists() else System.objects.all()
            context["systems"] = systems_qs.annotate(
                total_issues_count=Count('issues', filter=Q(issues__target_team=team)),
                open_issues_count=Count('issues', filter=Q(issues__target_team=team, issues__status='open'))
            )
            context["team_label"]         = dict(Issue.TargetTeam.choices).get(team, team)
            self.template_name = "core/member_dashboard.html"
            return context

        # ── Admin: full analytic dashboard ──
        stats = Issue.objects.aggregate(
            total=Count("id"),
            open=Count("id", filter=Q(status="open")),
            in_progress=Count("id", filter=Q(status="in_progress")),
            resolved=Count("id", filter=Q(status="resolved")),
            closed=Count("id", filter=Q(status="closed")),
            reopened=Count("id", filter=Q(status="reopened")),
            critical=Count("id", filter=Q(priority="critical")),
            high=Count("id", filter=Q(priority="high")),
            medium=Count("id", filter=Q(priority="medium")),
            low=Count("id", filter=Q(priority="low")),
            bug=Count("id", filter=Q(issue_type="bug")),
            security=Count("id", filter=Q(issue_type="security")),
            ui=Count("id", filter=Q(issue_type="ui")),
            frontend=Count("id", filter=Q(target_team="frontend")),
            backend=Count("id", filter=Q(target_team="backend")),
        )

        # 1. Weekly Activity Logic (Last 7 Days)
        seven_days_ago = timezone.now().date() - datetime.timedelta(days=6)
        daily_stats = (
            Issue.objects.filter(created_at__date__gte=seven_days_ago)
            .values('created_at__date')
            .annotate(
                new=Count('id'),
                resolved=Count('id', filter=Q(status='resolved'))
            )
            .order_by('created_at__date')
        )
        day_labels, new_series, resolved_series = [], [], []
        for i in range(7):
            d = seven_days_ago + datetime.timedelta(days=i)
            day_labels.append(date_format(d, "D"))  # Localized short day
            match = next((x for x in daily_stats if x['created_at__date'] == d), None)
            new_series.append(match['new'] if match else 0)
            resolved_series.append(match['resolved'] if match else 0)
        
        # 2. Longitudinal Trend (6 Months)
        trend_labels, trend_series = [], []
        first_day = timezone.now().date().replace(day=1)
        for i in range(5, -1, -1):
            # Calculate roughly 6 months ago
            d = first_day - datetime.timedelta(days=i*30)
            month_start = d.replace(day=1)
            month_end = (month_start + datetime.timedelta(days=32)).replace(day=1) - datetime.timedelta(days=1)
            
            trend_labels.append(date_format(month_start, "M Y")) # Localized Month Year
            count = Issue.objects.filter(created_at__date__range=(month_start, month_end)).count()
            trend_series.append(count)

        # Sparkline Data (Last 7 Days Trend)
        seven_days_ago = timezone.now().date() - datetime.timedelta(days=6)
        daily_trends = (
            Issue.objects.filter(created_at__date__gte=seven_days_ago)
            .values('created_at__date')
            .annotate(
                total=Count('id'),
                open=Count('id', filter=Q(status='open')),
                progress=Count('id', filter=Q(status='in_progress')),
                resolved=Count('id', filter=Q(status='resolved')),
            )
            .order_by('created_at__date')
        )
        total_spark, open_spark, prog_spark, res_spark = [], [], [], []
        for i in range(7):
            d = seven_days_ago + datetime.timedelta(days=i)
            match = next((x for x in daily_trends if x['created_at__date'] == d), None)
            total_spark.append(match['total'] if match else 0)
            open_spark.append(match['open'] if match else 0)
            prog_spark.append(match['progress'] if match else 0)
            res_spark.append(match['resolved'] if match else 0)
        
        context.update({
            "spark_total": json.dumps(total_spark),
            "spark_open": json.dumps(open_spark),
            "spark_progress": json.dumps(prog_spark),
            "spark_resolved": json.dumps(res_spark),
            "chart_stacked_labels": json.dumps(day_labels),
            "chart_stacked_new": json.dumps(new_series),
            "chart_stacked_resolved": json.dumps(resolved_series),
        })

        # 2. System Distribution (Donut - Top 5)
        system_stats = Issue.objects.values('system__name').annotate(count=Count('id')).order_by('-count')[:5]
        context.update({
            "chart_sys_labels": json.dumps([s['system__name'] or str(_("Other")) for s in system_stats]),
            "chart_sys_series": json.dumps([s['count'] for s in system_stats]),
        })

        # 3. Monthly Trend (Area - Last 6 Months)
        six_months_ago = timezone.now() - datetime.timedelta(days=180)
        monthly_qs = (
            Issue.objects.filter(created_at__gte=six_months_ago)
            .annotate(month=TruncMonth('created_at'))
            .values('month').annotate(count=Count('id')).order_by('month')
        )
        m_labels, m_series = [], []
        for entry in monthly_qs:
            m_labels.append(calendar.month_name[entry['month'].month][:3])
            m_series.append(entry['count'])
        context.update({
            "chart_trend_labels": json.dumps(m_labels),
            "chart_trend_series": json.dumps(m_series),
        })

        # 4. Priority Breakdown (Polar Area)
        p_labels = [str(_("Critical")), str(_("High")), str(_("Medium")), str(_("Low"))]
        p_series = [stats["critical"], stats["high"], stats["medium"], stats["low"]]
        context.update({
            "chart_priority_labels": json.dumps(p_labels),
            "chart_priority_series": json.dumps(p_series),
        })

        # 5. Issue Type (Donut)
        t_labels = [str(_("Bug")), str(_("Security")), str(_("UI"))]
        t_series = [stats["bug"], stats["security"], stats["ui"]]
        context.update({
            "chart_type_labels": json.dumps(t_labels),
            "chart_type_series": json.dumps(t_series),
        })

        # 6. Team Comparison (Radar/Bar)
        context.update({
            "chart_team_labels": json.dumps([str(_("FrontEnd")), str(_("BackEnd"))]),
            "chart_team_series": json.dumps([stats["frontend"], stats["backend"]]),
        })

        # 7. Resolution Rate & Growth
        resolved_and_closed = stats["resolved"] + stats["closed"]
        context["resolution_rate"] = round((stats["resolved"] / resolved_and_closed * 100) if resolved_and_closed > 0 else 0)
        
        last_month = timezone.now() - datetime.timedelta(days=30)
        prev_month = timezone.now() - datetime.timedelta(days=60)
        this_month_count = Issue.objects.filter(created_at__gte=last_month).count()
        prev_month_count = Issue.objects.filter(created_at__range=(prev_month, last_month)).count()
        if prev_month_count > 0:
            growth = round(((this_month_count - prev_month_count) / prev_month_count) * 100, 1)
        else:
            growth = 100.0 if this_month_count > 0 else 0.0
        context["report_growth"] = growth

        # Time-based greeting and extra stats
        now_hour = timezone.now().hour
        if 5 <= now_hour < 12:
            greeting = _("Good Morning")
        elif 12 <= now_hour < 18:
            greeting = _("Good Afternoon")
        else:
            greeting = _("Good Evening")
            
        # Comparison logic (Last 24h vs Average)
        now = timezone.now()
        today = now.date()
        this_week = today - datetime.timedelta(days=7)
        last_24h = now - datetime.timedelta(days=1)
        resolved_24h = Issue.objects.filter(status='resolved', updated_at__gte=last_24h).count()
        avg_resolved_daily = round(stats["resolved"] / max(1, (timezone.now() - Issue.objects.order_by('created_at').first().created_at).days) if stats["total"] > 0 else 0)
        
        context.update({
            "greeting": greeting,
            "resolved_24h": resolved_24h,
            "is_performing_well": resolved_24h >= avg_resolved_daily,
            "today_count": Issue.objects.filter(created_at__date=today).count(),
            "week_count": Issue.objects.filter(created_at__date__gte=this_week).count(),
            "total_issues": stats["total"],
            "open_issues": stats["open"],
            "in_progress_issues": stats["in_progress"],
            "resolved_issues": stats["resolved"],
            "closed_issues": stats["closed"],
            "critical_issues": stats["critical"],
            "high_issues": stats["high"],
            "medium_issues": stats["medium"],
            "low_issues": stats["low"],
            "bug_count": stats["bug"],
            "security_count": stats["security"],
            "ui_count": stats["ui"],
            "frontend_count": stats["frontend"],
            "backend_count": stats["backend"],
        })

        context["recent_issues"] = (
            Issue.objects.select_related("system", "reported_by").order_by("-created_at")[:8]
        )
        context["pending_reviews"] = (
            Issue.objects.filter(status="resolved").select_related("system", "reported_by").order_by("-updated_at")[:5]
        )
        context["latest_logs"] = IssueLog.objects.select_related('issue', 'changed_by').order_by('-created_at')[:6]
        return context


# ──────────────────────────────────────────────
# Issue Views
# ──────────────────────────────────────────────
class IssueListView(LoginRequiredMixin, ListView):
    model = Issue
    template_name = "core/issues/issue_list.html"
    context_object_name = "issues"
    paginate_by = 15

    def get_queryset(self):
        user = self.request.user
        qs = Issue.objects.select_related(
            "system", "screen", "reported_by", "assigned_to"
        ).order_by("-created_at")

        # ── FrontEnd / BackEnd: see only their team's issues ──
        if not user.is_admin:
            user_systems = System.objects.filter(groups__user=user).distinct()
            # Priority: filter by role
            qs = qs.filter(target_team=user.role)
            # Flexibility: restrict by system only if user is in groups
            if user_systems.exists():
                qs = qs.filter(system__in=user_systems)

        # Filters (shared for all roles)
        status     = self.request.GET.get("status")
        priority   = self.request.GET.get("priority")
        issue_type = self.request.GET.get("issue_type")
        search     = self.request.GET.get("search")

        if status:
            qs = qs.filter(status=status)
        if priority:
            qs = qs.filter(priority=priority)
        if issue_type:
            qs = qs.filter(issue_type=issue_type)
        if search:
            qs = qs.filter(
                Q(title__icontains=search) | Q(description__icontains=search)
            )
        return qs

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        context["filter_form"] = IssueFilterForm(self.request.GET)
        return context


class IssueCreateView(LoginRequiredMixin, CreateView):
    model = Issue
    form_class = IssueForm
    template_name = "core/issues/issue_form.html"
    success_url = reverse_lazy("issue-list")

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        context["page_title"] = _("New Error")
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.reported_by = self.request.user
        # Auto-set target_team for frontend/backend users
        if not self.request.user.is_admin:
            form.instance.target_team = self.request.user.role
        response = super().form_valid(form)
        IssueLog.objects.create(
            issue=self.object,
            action=_("Error Created"),
            new_value=_("Error '%(title)s' created for team: %(team)s") % {
                "title": self.object.title,
                "team": self.object.get_target_team_display()
            },
            changed_by=self.request.user,
        )
        messages.success(self.request, _("Error '%s' created successfully.") % self.object.title)
        return response


class IssueDetailView(LoginRequiredMixin, DetailView):
    model = Issue
    template_name = "core/issues/issue_detail.html"
    context_object_name = "issue"

    def get_queryset(self):
        user = self.request.user
        qs = Issue.objects.select_related("system", "screen", "reported_by", "assigned_to")
        if not user.is_admin:
            user_systems = System.objects.filter(groups__user=user).distinct()
            qs = qs.filter(target_team=user.role)
            if user_systems.exists():
                qs = qs.filter(system__in=user_systems)
        return qs

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        context["comments"] = self.object.comments.select_related("user").order_by("created_at")
        context["logs"] = self.object.logs.select_related("changed_by").order_by("-created_at")
        context["comment_form"] = CommentForm()
        return context


class IssueUpdateView(AdminRequiredMixin, UpdateView):
    model = Issue
    form_class = IssueForm
    template_name = "core/issues/issue_form.html"

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        context["page_title"] = _("Edit Error: %(title)s") % {"title": self.object.title}
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse_lazy("issue-detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        old_instance = Issue.objects.get(pk=self.object.pk)
        response = super().form_valid(form)
        tracked_fields = ["status", "priority", "assigned_to", "issue_type", "target_team"]
        for field in tracked_fields:
            old_val = str(getattr(old_instance, field))
            new_val = str(getattr(self.object, field))
            if old_val != new_val:
                field_name = field.replace('_', ' ').title()
                IssueLog.objects.create(
                    issue=self.object,
                    action=_("%(field)s Changed") % {"field": _(field_name)},
                    old_value=old_val,
                    new_value=new_val,
                    changed_by=self.request.user,
                )
        messages.success(self.request, _("Error '%s' updated successfully.") % self.object.title)
        return response


class IssueDeleteView(AdminRequiredMixin, DeleteView):
    model = Issue
    template_name = "core/issues/issue_confirm_delete.html"
    success_url = reverse_lazy("issue-list")

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        return context

    def form_valid(self, form):
        messages.success(self.request, _("Error '%s' deleted successfully.") % self.get_object().title)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("dashboard")


class UserProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = "core/users/profile.html"
    success_url = reverse_lazy("user-profile")

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        context['password_form'] = PasswordChangeForm(user=self.request.user)
        return context

    def form_valid(self, form):
        messages.success(self.request, _("Profile updated successfully."))
        return super().form_valid(form)


class UserPasswordChangeView(LoginRequiredMixin, UpdateView):
    """Handles password change POST submission from the profile page."""

    def post(self, request, *args, **kwargs):
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)  # Keep session alive
            messages.success(request, _("Password changed successfully."))
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
        return redirect("user-profile")

# ──────────────────────────────────────────────
# AJAX Operations
# ──────────────────────────────────────────────
@login_required
def update_issue_status(request, pk):
    if not request.user.is_admin:
        return JsonResponse({"success": False, "error": "Unauthorized"}, status=403)
        
    if request.method == "POST":
        issue = get_object_or_404(Issue, pk=pk)
        new_status = request.POST.get("status")
        
        if new_status in dict(Issue.Status.choices):
            old_status = issue.get_status_display()
            issue.status = new_status
            issue.save()
            
            # Create Log entry
            IssueLog.objects.create(
                issue=issue,
                action=_("Status Changed (Inline)"),
                old_value=old_status,
                new_value=issue.get_status_display(),
                changed_by=request.user,
            )
            
            return JsonResponse({"success": True, "new_status": issue.get_status_display()})
            
    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)


@login_required
def quick_resolve_issue(request, pk):
    """Allows developers to mark an issue as resolved with a single click."""
    issue = get_object_or_404(Issue, pk=pk)
    
    # Permission check: Admin or member of the target team
    if not request.user.is_admin and issue.target_team != request.user.role:
        messages.error(request, _("You are not authorized to resolve this issue."))
        return redirect("issue-list")
        
    if issue.status in [Issue.Status.RESOLVED, Issue.Status.CLOSED]:
        messages.info(request, _("This issue is already resolved or closed."))
        return redirect("issue-list")

    old_status = issue.get_status_display()
    issue.status = Issue.Status.RESOLVED
    issue.resolution = Issue.Resolution.FIXED
    issue.save()
    
    # Create Log entry
    IssueLog.objects.create(
        issue=issue,
        action=_("Quick Resolve"),
        old_value=old_status,
        new_value=issue.get_status_display(),
        changed_by=request.user,
    )
    
    messages.success(request, _("Excellent! Issue #%(id)s has been marked as Resolved.") % {"id": issue.pk})
    
    # Redirect back to the previous page or issue list
    return redirect(request.META.get('HTTP_REFERER', 'issue-list'))


# ──────────────────────────────────────────────
# Comment View
# ──────────────────────────────────────────────
class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        issue = get_object_or_404(Issue, pk=self.kwargs["issue_pk"])
        form.instance.issue = issue
        form.instance.user = self.request.user
        
        # Save the comment manually to avoid CreateView's automatic redirect logic
        self.object = form.save()
        
        IssueLog.objects.create(
            issue=issue,
            action=_("Comment Added"),
            new_value=form.instance.content[:100],
            changed_by=self.request.user,
        )
        messages.success(self.request, _("Comment added successfully."))
        return redirect("issue-detail", pk=issue.pk)

    def form_invalid(self, form):
        return redirect("issue-detail", pk=self.kwargs["issue_pk"])


# ──────────────────────────────────────────────
# System Views (Admin Only)
# ──────────────────────────────────────────────
class SystemListView(AdminRequiredMixin, ListView):
    model = System
    template_name = "core/systems/system_list.html"
    context_object_name = "systems"

    def get_queryset(self):
        return System.objects.annotate(
            screen_count=Count("screens"),
            group_count=Count("groups"),
            issue_count=Count("issues"),
        )

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        return context


class SystemCreateView(AdminRequiredMixin, CreateView):
    model = System
    form_class = SystemForm
    template_name = "core/systems/system_form.html"
    success_url = reverse_lazy("system-list")

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        context["page_title"] = _("Add New System")
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _("System '%s' created successfully.") % self.object.name)
        return response


class SystemUpdateView(AdminRequiredMixin, UpdateView):
    model = System
    form_class = SystemForm
    template_name = "core/systems/system_form.html"
    success_url = reverse_lazy("system-list")

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        context["page_title"] = _("Edit System: %(name)s") % {"name": self.object.name}
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _("System '%s' updated successfully.") % self.object.name)
        return response


class SystemDeleteView(AdminRequiredMixin, DeleteView):
    model = System
    template_name = "core/systems/system_confirm_delete.html"
    success_url = reverse_lazy("system-list")

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        return context

    def form_valid(self, form):
        messages.success(self.request, _("System '%s' deleted successfully.") % self.get_object().name)
        return super().form_valid(form)


# ──────────────────────────────────────────────
# Group Views (Admin Only)
# ──────────────────────────────────────────────
class GroupListView(AdminRequiredMixin, ListView):
    model = Group
    template_name = "core/groups/group_list.html"
    context_object_name = "groups"

    def get_queryset(self):
        return Group.objects.annotate(
            member_count=Count("user"),
            system_count=Count("systems")
        )

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        return context


class GroupCreateView(AdminRequiredMixin, CreateView):
    model = Group
    form_class = GroupForm
    template_name = "core/groups/group_form.html"
    success_url = reverse_lazy("group-list")

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        context["page_title"] = _("Add New Group")
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _("Group '%s' created successfully.") % self.object.name)
        return response


class GroupUpdateView(AdminRequiredMixin, UpdateView):
    model = Group
    form_class = GroupForm
    template_name = "core/groups/group_form.html"
    success_url = reverse_lazy("group-list")

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        context["page_title"] = _("Edit Group: %(name)s") % {"name": self.object.name}
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _("Group '%s' updated successfully.") % self.object.name)
        return response


class GroupDeleteView(AdminRequiredMixin, DeleteView):
    model = Group
    template_name = "core/groups/group_confirm_delete.html"
    success_url = reverse_lazy("group-list")

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        return context

    def form_valid(self, form):
        messages.success(self.request, _("Group '%s' deleted successfully.") % self.get_object().name)
        return super().form_valid(form)


# ──────────────────────────────────────────────
# Screen Views (Admin Only)
# ──────────────────────────────────────────────
class ScreenListView(AdminRequiredMixin, ListView):
    model = Screen
    template_name = "core/screens/screen_list.html"
    context_object_name = "screens"

    def get_queryset(self):
        return Screen.objects.select_related("system")

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        return context


class ScreenCreateView(AdminRequiredMixin, CreateView):
    model = Screen
    form_class = ScreenForm
    template_name = "core/screens/screen_form.html"
    success_url = reverse_lazy("screen-list")

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        context["page_title"] = _("Add New Screen")
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _("Screen '%s' created successfully.") % self.object.name)
        return response


class ScreenUpdateView(AdminRequiredMixin, UpdateView):
    model = Screen
    form_class = ScreenForm
    template_name = "core/screens/screen_form.html"
    success_url = reverse_lazy("screen-list")

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        context["page_title"] = _("Edit Screen: %(name)s") % {"name": self.object.name}
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _("Screen '%s' updated successfully.") % self.object.name)
        return response


class ScreenDeleteView(AdminRequiredMixin, DeleteView):
    model = Screen
    template_name = "core/screens/screen_confirm_delete.html"
    success_url = reverse_lazy("screen-list")

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        return context

    def form_valid(self, form):
        messages.success(self.request, _("Screen '%s' deleted successfully.") % self.get_object().name)
        return super().form_valid(form)


# ──────────────────────────────────────────────
# User Views (Admin Only)
# ──────────────────────────────────────────────
class UserListView(AdminRequiredMixin, ListView):
    model = User
    template_name = "core/users/user_list.html"
    context_object_name = "users_list"

    def get_queryset(self):
        return User.objects.prefetch_related("groups").exclude(is_superuser=True)

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        return context


class UserCreateView(AdminRequiredMixin, CreateView):
    model = User
    form_class = UserForm
    template_name = "core/users/user_form.html"
    success_url = reverse_lazy("user-list")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _("User '%s' created successfully.") % self.object.username)
        return response

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        context["page_title"] = _("Create User")
        return context


class UserUpdateView(AdminRequiredMixin, UpdateView):
    model = User
    form_class = UserForm
    template_name = "core/users/user_form.html"
    success_url = reverse_lazy("user-list")

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        context["page_title"] = _("Edit User: %(username)s") % {"username": self.object.username}
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _("User '%s' updated successfully.") % self.object.username)
        return response


class UserDeleteView(AdminRequiredMixin, DeleteView):
    model = User
    template_name = "core/users/user_confirm_delete.html"
    success_url = reverse_lazy("user-list")

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        return context

    def form_valid(self, form):
        messages.success(self.request, _("User '%s' deleted successfully.") % self.get_object().username)
        return super().form_valid(form)


# ──────────────────────────────────────────────
# AJAX: Get Screens by System
# ──────────────────────────────────────────────
def load_screens(request):
    # Support both single system_id and list system_id[] (for multi-select)
    system_ids = request.GET.getlist("system_id[]")
    if not system_ids:
        system_id = request.GET.get("system_id")
        system_ids = [system_id] if system_id else []

    qs = Screen.objects.filter(system_id__in=system_ids)

    # Filter screens for frontend/backend users (Flexible: only if they have system groups)
    if request.user.is_authenticated and not request.user.is_admin:
        user_systems = System.objects.filter(groups__user=request.user)
        if user_systems.exists():
            qs = qs.filter(groups__user=request.user).distinct()

    screens = qs.values("id", "name")
    return JsonResponse(list(screens), safe=False)


@login_required
def mark_notification_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notification.is_read = True
    notification.save()
    return redirect("issue-detail", pk=notification.issue.pk)


# ──────────────────────────────────────────────
# Report Views
# ──────────────────────────────────────────────
class ReportFilterView(AdminRequiredMixin, TemplateView):
    template_name = "core/reports/report_filter.html"

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        user = self.request.user
        context["form"] = ReportFilterForm(self.request.GET or None, user=user)
        
        # Filter stats for non-admins
        issues_qs = Issue.objects.all()
        if not user.is_admin:
            issues_qs = issues_qs.filter(target_team=user.role)
            user_systems = System.objects.filter(groups__user=user)
            if user_systems.exists():
                issues_qs = issues_qs.filter(system__in=user_systems)

        context["open_count"] = issues_qs.filter(status=Issue.Status.OPEN).count()
        context["resolved_count"] = issues_qs.filter(status=Issue.Status.RESOLVED).count()
        context["frontend_count"] = issues_qs.filter(target_team=Issue.TargetTeam.FRONTEND).count()
        context["backend_count"] = issues_qs.filter(target_team=Issue.TargetTeam.BACKEND).count()
        return context


class ReportPrintView(AdminRequiredMixin, ListView):
    model = Issue
    template_name = "core/reports/report_print.html"
    context_object_name = "issues"

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset().select_related("system", "screen", "reported_by").order_by("-created_at")
        
        # ── Role-based restriction ──
        if not user.is_admin:
            queryset = queryset.filter(target_team=user.role)
            user_systems = System.objects.filter(groups__user=user).distinct()
            if user_systems.exists():
                queryset = queryset.filter(system__in=user_systems)

        # Apply filters from GET parameters
        start_date = self.request.GET.get("start_date")
        end_date = self.request.GET.get("end_date")
        system_id = self.request.GET.get("system")
        status = self.request.GET.get("status")
        priority = self.request.GET.get("priority")
        target_team = self.request.GET.get("target_team")

        if start_date:
            queryset = queryset.filter(created_at__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__date__lte=end_date)
        if system_id:
            queryset = queryset.filter(system_id=system_id)
        if status:
            queryset = queryset.filter(status=status)
        if priority:
            queryset = queryset.filter(priority=priority)
        if target_team:
            queryset = queryset.filter(target_team=target_team)
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add metadata for the report header
        context["report_date"] = timezone.now()
        context["filter_system"] = System.objects.filter(pk=self.request.GET.get("system")).first() if self.request.GET.get("system") else None
        
        # Proper lookup for status display name
        status_val = self.request.GET.get("status")
        context["filter_status"] = dict(Issue.Status.choices).get(status_val) if status_val else None
        
        # Add target team name to context
        team_val = self.request.GET.get("target_team")
        context["filter_team"] = dict(Issue.TargetTeam.choices).get(team_val) if team_val else None
        
        return context
