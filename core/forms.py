from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _

from .models import Issue, Comment, System, Screen, User
from django.contrib.auth.models import Group

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit


# ──────────────────────────────────────────────
# Auth Forms
# ──────────────────────────────────────────────
class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label=_("Username"),
        widget=forms.TextInput(
            attrs={
                "placeholder": _("Enter your username"),
                "autofocus": True,
            }
        )
    )
    password = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "············",
            }
        )
    )


# ──────────────────────────────────────────────
# User Management Form
# ──────────────────────────────────────────────
class UserForm(forms.ModelForm):
    password = forms.CharField(
        label=_("Password"),
        required=False,
        widget=forms.PasswordInput(attrs={"placeholder": _("Leave blank to keep same password")}),
        help_text=_("Provide a password to set/change it. Leave blank to keep the existing password.")
    )

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "role", "groups", "is_active"]
        widgets = {
            "username": forms.TextInput(),
            "email": forms.EmailInput(),
            "first_name": forms.TextInput(),
            "last_name": forms.TextInput(),
            "role": forms.Select(),
            "groups": forms.SelectMultiple(attrs={"class": "select2", "data-placeholder": _("Select groups")}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            # If creating a new user, password is required
            self.fields['password'].required = True
            self.fields['password'].help_text = _("Required for new users.")

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                Column('username', css_class='form-group col-md-6 mb-3'),
                Column('email', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
            Row(
                Column('first_name', css_class='form-group col-md-6 mb-3'),
                Column('last_name', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
            Row(
                Column('role', css_class='form-group col-md-6 mb-3'),
                Column('password', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
            Row(
                Column('groups', css_class='form-group col-md-6 mb-3'),
                Column('is_active', css_class='form-group col-md-6 mb-3 d-flex align-items-center mt-4'),
                css_class='form-row'
            ),
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("password")
        if password:
            user.set_password(password)
        if commit:
            user.save()
            self.save_m2m() # Important for many-to-many fields like groups
        return user


# ──────────────────────────────────────────────
# Issue Form
# ──────────────────────────────────────────────
class IssueForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = [
            "title",
            "description",
            "system",
            "screen",
            "target_team",
            "assigned_to",
            "issue_type",
            "priority",
            "status",
            "steps_to_reproduce",
            "expected_result",
            "actual_result",
            "resolution",
            "root_cause",
            "image",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": _("Error title")}),
            "description": forms.Textarea(attrs={"rows": 4, "placeholder": _("Describe the error...")}),
            "system": forms.Select(),
            "screen": forms.Select(),
            "target_team": forms.Select(),
            "assigned_to": forms.Select(),
            "issue_type": forms.Select(),
            "priority": forms.Select(),
            "status": forms.Select(),
            "steps_to_reproduce": forms.Textarea(attrs={"rows": 3, "placeholder": _("Steps to reproduce...")}),
            "expected_result": forms.Textarea(attrs={"rows": 3, "placeholder": _("Expected result...")}),
            "actual_result": forms.Textarea(attrs={"rows": 3, "placeholder": _("Actual result...")}),
            "resolution": forms.Select(),
            "root_cause": forms.Textarea(attrs={"rows": 3, "placeholder": _("Explain the root cause of this error...")}),
            "image": forms.ClearableFileInput(),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # ── Global Hiding for Create View ──
        # These fields are only relevant during resolution/update
        if not self.instance.pk:
            create_hidden_fields = ["resolution", "root_cause", "status"]
            for field in create_hidden_fields:
                if field in self.fields:
                    del self.fields[field]

        # ── FrontEnd / BackEnd users ──
        if self.user and not self.user.is_admin:
            # Hide assigned_to — only admin assigns
            if "assigned_to" in self.fields:
                del self.fields["assigned_to"]

            # Hide target_team — auto-set from the user's role
            if "target_team" in self.fields:
                del self.fields["target_team"]

            # Filter systems to only those the user belongs to
            user_systems = System.objects.filter(groups__user=self.user).distinct()
            self.fields["system"].queryset = user_systems
            if user_systems.count() == 1:
                self.initial["system"] = user_systems.first()

            # Filter screens to only those the user belongs to
            self.fields["screen"].queryset = Screen.objects.filter(
                groups__user=self.user
            ).distinct()

        # ── Admin ──
        else:
            if "assigned_to" in self.fields:
                self.fields["assigned_to"].required = False
                self.fields["assigned_to"].queryset = User.objects.all()
            self.fields["screen"].queryset = Screen.objects.none()

        # Dependent dropdown for screens (works for both roles)
        if "system" in self.data:
            try:
                system_id = int(self.data.get("system"))
                qs = Screen.objects.filter(system_id=system_id)
                if self.user and not self.user.is_admin:
                    qs = qs.filter(groups__user=self.user).distinct()
                self.fields["screen"].queryset = qs
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.system:
            qs = self.instance.system.screens.all()
            if self.user and not self.user.is_admin:
                qs = qs.filter(groups__user=self.user).distinct()
            self.fields["screen"].queryset = qs

        # ── FormHelper Layout ──
        self.helper = FormHelper()
        self.helper.form_tag = False
        
        layout_items = []
        layout_items.append(Row(Column('title', css_class='form-group col-md-12 mb-3')))
        layout_items.append(Row(Column('description', css_class='form-group col-md-12 mb-3')))
        
        sys_scr_cols = []
        if 'system' in self.fields: sys_scr_cols.append(Column('system', css_class='form-group col-md-6 mb-3'))
        if 'screen' in self.fields: sys_scr_cols.append(Column('screen', css_class='form-group col-md-6 mb-3'))
        if sys_scr_cols: layout_items.append(Row(*sys_scr_cols, css_class='form-row'))
        
        type_prio_cols = []
        if 'issue_type' in self.fields: type_prio_cols.append(Column('issue_type', css_class='form-group col-md-6 mb-3'))
        if 'priority' in self.fields: type_prio_cols.append(Column('priority', css_class='form-group col-md-6 mb-3'))
        if type_prio_cols: layout_items.append(Row(*type_prio_cols, css_class='form-row'))

        team_assign_cols = []
        if 'target_team' in self.fields: team_assign_cols.append(Column('target_team', css_class='form-group col-md-6 mb-3'))
        if 'assigned_to' in self.fields: team_assign_cols.append(Column('assigned_to', css_class='form-group col-md-6 mb-3'))
        if team_assign_cols: layout_items.append(Row(*team_assign_cols, css_class='form-row'))
        
        if 'status' in self.fields:
            layout_items.append(Row(Column('status', css_class='form-group col-md-6 mb-3')))
            
        layout_items.append(Row(Column('steps_to_reproduce', css_class='form-group col-md-12 mb-3')))
        
        res_cols = []
        if 'expected_result' in self.fields: res_cols.append(Column('expected_result', css_class='form-group col-md-6 mb-3'))
        if 'actual_result' in self.fields: res_cols.append(Column('actual_result', css_class='form-group col-md-6 mb-3'))
        if res_cols: layout_items.append(Row(*res_cols, css_class='form-row'))
        
        if 'image' in self.fields:
            layout_items.append(Row(Column('image', css_class='form-group col-md-12 mb-3')))
            
        resol_cols = []
        if 'resolution' in self.fields: resol_cols.append(Column('resolution', css_class='form-group col-md-12 mb-3'))
        if 'root_cause' in self.fields: resol_cols.append(Column('root_cause', css_class='form-group col-md-12 mb-3'))
        if resol_cols: layout_items.append(Row(*resol_cols, css_class='form-row'))

        self.helper.layout = Layout(*layout_items)



class IssueFilterForm(forms.Form):
    STATUS_CHOICES = [("", _("All Statuses"))] + list(Issue.Status.choices)
    PRIORITY_CHOICES = [("", _("All Priorities"))] + list(Issue.Priority.choices)
    TYPE_CHOICES = [("", _("All Types"))] + list(Issue.IssueType.choices)

    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "form-select-sm"}),
    )
    priority = forms.ChoiceField(
        choices=PRIORITY_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "form-select-sm"}),
    )
    issue_type = forms.ChoiceField(
        choices=TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "form-select-sm"}),
    )
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control-sm", "placeholder": _("Search issues...")}),
    )


# ──────────────────────────────────────────────
# Comment Form
# ──────────────────────────────────────────────
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": _("Write a comment..."),
                }
            ),
        }


# ──────────────────────────────────────────────
# System Form
# ──────────────────────────────────────────────
class SystemForm(forms.ModelForm):
    class Meta:
        model = System
        fields = ["name", "description", "groups", "is_active"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": _("System name")}),
            "description": forms.Textarea(attrs={"rows": 3, "placeholder": _("System description...")}),
            "groups": forms.SelectMultiple(attrs={"class": "select2", "data-placeholder": _("Assign to groups")}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(Column('name', css_class='form-group col-md-12 mb-3')),
            Row(Column('description', css_class='form-group col-md-12 mb-3')),
            Row(
                Column('groups', css_class='form-group col-md-6 mb-3'),
                Column('is_active', css_class='form-group col-md-6 mb-3 d-flex align-items-center mt-4'),
                css_class='form-row'
            ),
        )


# ──────────────────────────────────────────────
# Screen Form
# ──────────────────────────────────────────────
class ScreenForm(forms.ModelForm):
    class Meta:
        model = Screen
        fields = ["system", "name", "groups"]
        widgets = {
            "system": forms.Select(),
            "name": forms.TextInput(attrs={"placeholder": _("Screen name")}),
            "groups": forms.SelectMultiple(attrs={"class": "select2", "data-placeholder": _("Assign to groups")}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                Column('system', css_class='form-group col-md-6 mb-3'),
                Column('name', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
            Row(Column('groups', css_class='form-group col-md-12 mb-3')),
        )


# ──────────────────────────────────────────────
# Group Form (Custom management for Django Groups)
# ──────────────────────────────────────────────
class GroupForm(forms.ModelForm):
    systems = forms.ModelMultipleChoiceField(
        queryset=System.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={"class": "select2", "data-placeholder": _("Select systems")}),
        label=_("Systems Accessible")
    )
    screens = forms.ModelMultipleChoiceField(
        queryset=Screen.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={"class": "select2", "data-placeholder": _("Select screens")}),
        label=_("Specific Screens Assigned")
    )

    class Meta:
        model = Group
        fields = ["name", "systems", "screens"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": _("Group name")}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            systems = self.instance.systems.all()
            self.fields["systems"].initial = systems
            self.fields["screens"].initial = self.instance.screens.all()
            
            # If editing, filter available screens to only those in the chosen systems
            if systems.exists():
                self.fields["screens"].queryset = Screen.objects.filter(system__in=systems)
            else:
                self.fields["screens"].queryset = Screen.objects.all() # Or none if preferred
        
        # Handle POST data filtering if validation fails
        if self.data and self.data.getlist("systems"):
             try:
                 system_ids = self.data.getlist("systems")
                 self.fields["screens"].queryset = Screen.objects.filter(system_id__in=system_ids)
             except (ValueError, TypeError):
                 pass

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(Column('name', css_class='form-group col-md-12 mb-3')),
            Row(
                Column('systems', css_class='form-group col-md-6 mb-3'),
                Column('screens', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
        )

    def save(self, commit=True):
        group = super().save(commit=commit)
        if commit:
            group.systems.set(self.cleaned_data["systems"])
            group.screens.set(self.cleaned_data["screens"])
        return group


# ──────────────────────────────────────────────
# Report Filter Form
# ──────────────────────────────────────────────
class ReportFilterForm(forms.Form):
    start_date = forms.DateField(
        label=_("Start Date"),
        required=False,
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"})
    )
    end_date = forms.DateField(
        label=_("End Date"),
        required=False,
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"})
    )
    system = forms.ModelChoiceField(
        queryset=System.objects.all(),
        label=_("System"),
        required=False,
        empty_label=_("All Systems"),
        widget=forms.Select(attrs={"class": "form-select"})
    )
    status = forms.ChoiceField(
        choices=[("", _("All Statuses"))] + Issue.Status.choices,
        label=_("Status"),
        required=False,
        widget=forms.Select(attrs={"class": "form-select"})
    )
    priority = forms.ChoiceField(
        choices=[("", _("All Priorities"))] + Issue.Priority.choices,
        label=_("Priority"),
        required=False,
        widget=forms.Select(attrs={"class": "form-select"})
    )
    target_team = forms.ChoiceField(
        choices=[("", _("All Teams"))] + Issue.TargetTeam.choices,
        label=_("Target Team"),
        required=False,
        widget=forms.Select(attrs={"class": "form-select"})
    )

# ──────────────────────────────────────────────
# User Profile Form
# ──────────────────────────────────────────────
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'avatar']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('first_name', css_class='form-group col-md-6 mb-3'),
                Column('last_name', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
            'email',
            'avatar',
            Submit('submit', _('Save Changes'), css_class='btn btn-primary mt-3')
        )

