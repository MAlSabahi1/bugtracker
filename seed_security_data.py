import os
import django
import random
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import User, Issue, System, Screen

def seed_security_data():
    print("Seeding Security data...")
    
    # 1. Create Security Users
    security_users = []
    for i in range(1, 6):
        username = f"security_user_{i}"
        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(
                username=username,
                password="password123",
                first_name=random.choice(["أحمد", "محمد", "علي", "سعد", "فهد"]),
                last_name=random.choice(["الأمني", "الحربي", "القحطاني", "العتيبي", "المالكي"]),
                role=User.Role.SECURITY,
                email=f"{username}@example.com"
            )
            security_users.append(user)
            print(f"Created Security User: {username}")
        else:
            security_users.append(User.objects.get(username=username))

    systems = list(System.objects.all())
    if not systems:
        print("No systems found. Please add systems first.")
        return

    # 2. Create Security Issues
    security_titles = [
        "ثغرة أمنية في نظام تسجيل الدخول",
        "محاولة وصول غير مصرح به للقاعدة",
        "تسريب بيانات في تقارير النظام",
        "تجاوز صلاحيات في شاشة الإعدادات",
        "خلل في تشفير كلمات المرور",
        "هجوم SQL Injection محتمل",
        "ضعف في بروتوكول المصادقة",
        "تجاوز حماية الـ CSRF",
        "كشف ملفات النظام الحساسة",
        "تعديل سجلات النشاط بشكل غير قانوني"
    ]
    
    security_descriptions = [
        "تم اكتشاف ثغرة تتيح للمهاجم تجاوز شاشة تسجيل الدخول باستخدام تقنيات حقن النصوص.",
        "تم رصد محاولات متكررة للوصول المباشر لقاعدة البيانات من عناوين IP خارجية.",
        "التقارير المطبوعة تحتوي على بيانات حساسة لا ينبغي أن تظهر لجميع المستخدمين.",
        "يمكن للمستخدمين العاديين الوصول لشاشة الإعدادات المتقدمة من خلال الرابط المباشر.",
        "النظام يستخدم خوارزمية تشفير ضعيفة يمكن كسرها بسهولة.",
        "شاشة البحث لا تقوم بتنقية المدخلات مما يعرضها لخطر حقن الأوامر البرمجية.",
        "هناك خلل في الجلسات يتيح انتحال شخصية مستخدم آخر.",
        "التطبيقات لا تطلب رمز التحقق في العمليات الحساسة.",
        "تم اكتشاف مسار يظهر ملفات الإعدادات السرية للمشروع.",
        "تم رصد حذف سجلات من Timeline دون وجود أثر لمن قام بذلك."
    ]

    admins = list(User.objects.filter(role=User.Role.ADMIN))
    if not admins:
        admins = [User.objects.filter(is_superuser=True).first()]

    for i in range(20):
        system = random.choice(systems)
        screens = list(system.screens.all())
        screen = random.choice(screens) if screens else None
        
        if not screen: continue
        
        reporter = random.choice(security_users + admins)
        assignee = random.choice(security_users)
        
        title = random.choice(security_titles) + f" #{i+1}"
        desc = random.choice(security_descriptions)
        
        issue = Issue.objects.create(
            title=title,
            description=desc,
            system=system,
            screen=screen,
            reported_by=reporter,
            assigned_to=assignee,
            issue_type=Issue.IssueType.SECURITY,
            priority=random.choice(Issue.Priority.choices)[0],
            status=random.choice(Issue.Status.choices)[0],
            target_team=Issue.TargetTeam.SECURITY,
            steps_to_reproduce="1. افتح الرابط المباشر\n2. أدخل الكود المرفق\n3. سيتم التجاوز",
            expected_result="يجب منع الوصول وإظهار رسالة خطأ",
            actual_result="يتم الدخول مباشرة للنظام"
        )
        print(f"Created Security Issue: {issue.title}")

    print("Seeding completed successfully.")

if __name__ == "__main__":
    seed_security_data()
