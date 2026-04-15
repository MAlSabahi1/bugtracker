import os
import django
import random

def populate():
    from core.models import System, Screen, User, Issue, Comment
    from django.contrib.auth.models import Group

    print("Starting database population...")

    # Create Groups
    groups = ['Admins', 'Developers', 'Testers', 'Managers']
    created_groups = []
    for g_name in groups:
        group, _ = Group.objects.get_or_create(name=g_name)
        created_groups.append(group)

    # Create Users
    print("Creating users...")
    users_data = [
        {"username": "admin_mock", "role": User.Role.ADMIN, "email": "admin@mock.com"},
        {"username": "frontend_dev1", "role": User.Role.FRONTEND, "email": "front1@mock.com"},
        {"username": "frontend_dev2", "role": User.Role.FRONTEND, "email": "front2@mock.com"},
        {"username": "backend_dev1", "role": User.Role.BACKEND, "email": "back1@mock.com"},
        {"username": "backend_dev2", "role": User.Role.BACKEND, "email": "back2@mock.com"},
    ]
    
    created_users = []
    for u_data in users_data:
        user, created = User.objects.get_or_create(username=u_data["username"], defaults={"role": u_data["role"], "email": u_data["email"]})
        if created:
            user.set_password('password123')
            user.save()
        created_users.append(user)

    # Create Systems & Screens
    print("Creating systems and screens...")
    systems_data = {
        "E-Commerce Platform": ["Homepage", "Product Listing", "Checkout", "User Profile", "Cart"],
        "HR Management": ["Dashboard", "Employee List", "Leave Requests", "Payroll"],
        "Inventory System": ["Warehouse Dashboard", "Stock Adjustment", "Supplier Management"]
    }
    
    created_systems = []
    created_screens = []

    for sys_name, screens in systems_data.items():
        system, _ = System.objects.get_or_create(name=sys_name, defaults={"description": f"Description for {sys_name}"})
        # add some groups
        system.groups.set(random.sample(created_groups, 2))
        created_systems.append(system)
        
        for screen_name in screens:
            screen, _ = Screen.objects.get_or_create(system=system, name=screen_name)
            screen.groups.set(random.sample(created_groups, 2))
            created_screens.append(screen)

    # Create Issues
    print("Creating issues...")
    issue_titles = [
        "Login button not working",
        "Page crashes on load",
        "Incorrect spelling on dashboard",
        "API returning 500 error",
        "Data not syncing properly",
        "Missing validation on email field",
        "Dark mode looks weird",
        "Performance is slow",
        "Session timeout too fast",
        "Export to CSV is broken"
    ]
    
    descriptions = [
        "When I click the button nothing happens. I checked the console and there is an error.",
        "The page just goes white and nothing loads. Please fix ASAP.",
        "There is a typo in the main header of the screen.",
        "When submitting the form, the API returns a 500 internal server error.",
    ]

    for i in range(30):
        sys = random.choice(created_systems)
        scr = random.choice([s for s in created_screens if s.system == sys])
        reporter = random.choice(created_users)
        assignee = random.choice(created_users + [None])
        
        issue = Issue.objects.create(
            title=f"{random.choice(issue_titles)} - {i+1}",
            description=random.choice(descriptions),
            system=sys,
            screen=scr,
            reported_by=reporter,
            assigned_to=assignee,
            issue_type=random.choice(Issue.IssueType.choices)[0],
            priority=random.choice(Issue.Priority.choices)[0],
            status=random.choice(Issue.Status.choices)[0],
            target_team=random.choice(Issue.TargetTeam.choices)[0],
            resolution=random.choice(Issue.Resolution.choices)[0] if random.random() > 0.5 else Issue.Resolution.UNRESOLVED
        )
        
        # Create Comments for Issue
        for _ in range(random.randint(0, 3)):
            Comment.objects.create(
                issue=issue,
                user=random.choice(created_users),
                content=f"This is a mock comment {random.randint(1, 100)} regarding this issue."
            )

    print("Successfully populated the database with mock data!")

if __name__ == '__main__':
    populate()
