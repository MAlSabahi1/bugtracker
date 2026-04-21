import os
import random
from datetime import timedelta
from django.utils import timezone
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from core.models import User, System, Screen, Issue, Comment, IssueLog, Notification

class Command(BaseCommand):
    help = 'Seeds the database with Arabic data'

    def handle(self, *args, **kwargs):
        self.stdout.write("Deleting existing data...")
        
        # Delete data in reverse dependency order
        Notification.objects.all().delete()
        IssueLog.objects.all().delete()
        Comment.objects.all().delete()
        Issue.objects.all().delete()
        Screen.objects.all().delete()
        System.objects.all().delete()
        User.objects.exclude(is_superuser=True).delete()
        Group.objects.all().delete()

        # Check if superuser exists, if not create one
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@example.com", "admin")
            self.stdout.write("Created superuser: admin / admin")
        admin_user = User.objects.get(username="admin")

        self.stdout.write("Creating Groups...")
        groups_data = [
            "مجموعة الموارد البشرية", "مجموعة المبيعات", "مجموعة المحاسبة", 
            "مجموعة الإدارة العليا", "مجموعة تقنية المعلومات", "مجموعة شؤون الطلاب"
        ]
        groups = []
        for g_name in groups_data:
            g, _ = Group.objects.get_or_create(name=g_name)
            groups.append(g)

        self.stdout.write("Creating Users (30+ users)...")
        arabic_names = [
            "أحمد علي", "محمد عبد الله", "فاطمة سعيد", "عمر محمود", "خالد يوسف",
            "سارة حسن", "نورة فهد", "طارق زياد", "منى عبد الرحمن", "ياسر صالح",
            "ريما ناصر", "عبد العزيز سعد", "هدى إبراهيم", "ماجد عبد العزيز", "نوف سالم",
            "زياد طارق", "هند منصور", "سليمان داود", "ليلى كمال", "رامي عادل",
            "سمير جلال", "دينا مجدي", "حسن مصطفى", "نادية عمر", "يوسف أحمد",
            "عبير محمود", "باسم فاروق", "شيرين عبد الله", "جمال سعيد", "وفاء حسام",
            "عصام شريف", "مروة نبيل", "كريم عثمان", "نهى عبد الحميد", "تامر شكري"
        ]
        users = []
        for i, name in enumerate(arabic_names):
            role = random.choice([User.Role.FRONTEND, User.Role.BACKEND])
            username = f"user_{i}"
            user = User.objects.create_user(
                username=username,
                password="password123",
                first_name=name.split()[0],
                last_name=name.split()[1] if len(name.split()) > 1 else "",
                role=role
            )
            # Assign random groups
            user.groups.add(*random.sample(groups, k=random.randint(1, 3)))
            users.append(user)
        
        users.append(admin_user)

        self.stdout.write("Creating Systems & Screens...")
        systems_data = {
            "نظام الموارد البشرية (HRMS)": ["شاشة ملفات الموظفين", "شاشة إعداد مسيرات الرواتب", "شاشة الحضور والانصراف", "شاشة طلبات الإجازات", "شاشة السلف والعهد", "لوحة القيادة للـ HR", "شاشة تقييم الأداء"],
            "نظام المبيعات ونقاط البيع (POS)": ["شاشة بيانات العملاء", "شاشة إصدار الفواتير", "شاشة عروض الأسعار", "شاشة المرتجعات", "شاشة تقارير المبيعات اليومية", "شاشة العروض والخصومات"],
            "نظام الحسابات العامة (ERP)": ["شاشة دليل الحسابات", "شاشة قيود اليومية", "شاشة ميزان المراجعة", "شاشة إهلاك الأصول", "شاشة الميزانية العمومية", "شاشة قائمة الدخل", "شاشة مراكز التكلفة", "شاشة إغلاق السنة المالية"],
            "نظام إدارة المستودعات (WMS)": ["شاشة تعريف الأصناف", "شاشة الجرد الفعلي", "شاشة حركات المخزون", "شاشة الموردين", "شاشة أوامر الصرف والاستلام", "شاشة تحويلات المخازن"],
            "النظام الأكاديمي الموحد": ["شاشة تسجيل الطلاب", "شاشة إدخال العلامات", "شاشة الجداول الدراسية", "شاشة خطط المقررات", "شاشة شؤون الخريجين", "شاشة الحضور والغياب للطلاب", "شاشة الرسوم الدراسية"]
        }
        
        systems = []
        screens = []
        for sys_name, screen_names in systems_data.items():
            sys = System.objects.create(name=sys_name, description=f"نظام متكامل لإدارة عمليات {sys_name}")
            sys.groups.add(*random.sample(groups, k=random.randint(1, 3)))
            systems.append(sys)
            for screen_name in screen_names:
                scr = Screen.objects.create(system=sys, name=screen_name)
                scr.groups.add(*random.sample(groups, k=random.randint(1, 2)))
                screens.append(scr)

        self.stdout.write("Creating Issues (60+ issues)...")
        issue_titles = [
            "خطأ عند حفظ الفاتورة الضريبية", "التصميم غير متجاوب في شاشة الموبايل", "النظام يتوقف عند تصدير التقرير إلى Excel",
            "تسرب في الذاكرة عند فتح قائمة العملاء الكبيرة", "خطأ في حساب نسبة ضريبة القيمة المضافة", "الزر لا يستجيب في شاشة تسجيل الدخول بعد المحاولة الثالثة",
            "كلمة المرور لا تتشفر بشكل صحيح في قاعدة البيانات", "اختفاء شريط البحث العلوي عند التمرير لأسفل", "بيانات الموظف تظهر فارغة في شاشة التعديل",
            "خطأ 500 عند رفع صورة الملف الشخصي بصيغة PNG", "اللون الأخضر غير واضح في الوضع الليلي", "تعليق النظام عند إدخال قيد محاسبي مزدوج غير متزن",
            "شجرة الحسابات لا تقوم بتحميل الأبناء للمستوى الثالث", "تسجيل خروج مفاجئ للمستخدم بعد 5 دقائق", "الأيقونات لا تظهر في متصفح سفاري الجوال",
            "خطأ في جمع إجمالي الرواتب الأساسية", "عدم القدرة على تصفية الحضور والانصراف بناءً على التاريخ المخصص", "خطأ في تنسيق طباعة كشف الحساب البنكي",
            "الصورة المصغرة للمنتج مشوهة في بطاقة الصنف", "زر 'إضافة صنف' يختفي بعد الضغط عليه مرة واحدة", "بطء شديد في عرض قائمة الطلاب المسجلين حديثاً",
            "رسالة خطأ غير مفهومة عند إدخال بيانات نصية في حقل رقمي", "البريد الإلكتروني لا يصل عند طلب استعادة كلمة المرور", "لا يمكن تغيير لغة الواجهة من الإعدادات",
            "تكرار الإشعارات المنبثقة أكثر من 3 مرات", "تصدير الإكسيل يخرج بخطوط غير مقروءة ورموز غريبة", "التاريخ يظهر بصيغة هجرية رغم اختيار الميلادي",
            "لا يمكن حذف مستخدم رغم توفر صلاحية الحذف", "خطأ في الاتصال بقاعدة البيانات عند ذروة الاستخدام", "الألوان غير متناسقة في شاشة عرض تقييم الأداء",
            "خطأ في عرض الرصيد الافتتاحي للحسابات الختامية", "عدم تحديث البيانات في الجدول بعد تعديلها إلا بعمل تحديث للصفحة", "خطأ 404 عند الانتقال للصفحة الثانية في الترقيم",
            "تأخر استجابة النظام في وقت استخراج كشوف الرواتب", "ظهور أكواد برمجية للمستخدم العادي عند فشل التحميل", "الرسوم البيانية في لوحة القيادة لا تعرض بيانات الشهر الحالي",
            "عدم القدرة على طباعة وصل استلام النقدية", "خطأ منطقي في احتساب خصومات التأخير", "تداخل نصوص القائمة الجانبية في الشاشات المتوسطة",
            "عدم إرسال إشعار للمدير المباشر عند طلب إجازة"
        ]

        descriptions = [
            "عند محاولة تنفيذ الإجراء يظهر خطأ غير متوقع في الكونسول (Console) ويتم إغلاق الشاشة أو تجمدها تماماً.",
            "الواجهة تتداخل مع بعضها البعض في الأجهزة اللوحية، يرجى مراجعة التنسيقات (CSS) وإصلاحها في أقرب وقت.",
            "يبدو أن هناك مشكلة في استعلام قاعدة البيانات يسبب بطء شديد يستغرق أكثر من 10 ثوانٍ لتحميل الصفحة.",
            "الميزة لا تعمل بالشكل المطلوب بناءً على مستند المتطلبات النظامية، نرجو التحقق من الشروط المنطقية.",
            "يرجى مراجعة الكود المتعلق بهذه الجزئية لوجود ثغرة أمنية محتملة تسمح بحقن أكواد (XSS).",
            "هناك مشكلة في توافقية المتصفح، تعمل جيداً على كروم ولكن تفشل تماماً على فايرفوكس وسفاري.",
            "البيانات المعروضة في الجدول لا تتطابق مع البيانات الموجودة في قاعدة البيانات، يبدو أن هناك مشكلة في الـ API."
        ]

        issues = []
        for i in range(70):
            sys = random.choice(systems)
            scr = random.choice(list(sys.screens.all()))
            reported_by = random.choice(users)
            assigned_to = random.choice(users) if random.random() > 0.2 else None
            status = random.choice(Issue.Status.values)
            priority = random.choice(Issue.Priority.values)
            issue_type = random.choice(Issue.IssueType.values)
            target_team = random.choice(Issue.TargetTeam.values)
            resolution = random.choice([r[0] for r in Issue.Resolution.choices if r[0] != 'unresolved']) if status in ['resolved', 'closed'] else Issue.Resolution.UNRESOLVED

            issue = Issue.objects.create(
                title=random.choice(issue_titles) + f" - تذكرة #{i+1000}",
                description=random.choice(descriptions),
                system=sys,
                screen=scr,
                reported_by=reported_by,
                assigned_to=assigned_to,
                issue_type=issue_type,
                priority=priority,
                status=status,
                target_team=target_team,
                resolution=resolution,
                steps_to_reproduce="1. تسجيل الدخول بصلاحيات مدير\n2. الانتقال إلى الشاشة المحددة من القائمة الجانبية\n3. تعبئة النموذج ببيانات تجريبية\n4. الضغط على زر الحفظ والتأكيد",
                expected_result="ظهور رسالة تفيد بنجاح العملية وتحديث الجدول بالبيانات الجديدة مباشرة.",
                actual_result="شاشة تتجمد ويظهر خطأ في الـ Network Tab يحمل الرمز 500 Internal Server Error.",
                root_cause="خطأ في تعريف المتغير في السطر 45 يؤدي لعدم القدرة على قراءة الـ Object." if status in ['resolved', 'closed'] else ""
            )
            
            # Randomize creation time within the last 45 days
            created_days_ago = random.randint(0, 45)
            created_time = timezone.now() - timedelta(days=created_days_ago, hours=random.randint(0, 23), minutes=random.randint(0, 59))
            
            Issue.objects.filter(pk=issue.pk).update(
                created_at=created_time,
                updated_at=created_time + timedelta(hours=random.randint(1, 72))
            )
            issue.refresh_from_db()
            issues.append(issue)

        self.stdout.write("Creating Comments and Logs...")
        comment_texts = [
            "تم استلام التذكرة وجاري التحقق من تفاصيل الخطأ.", 
            "نحتاج لتفاصيل إضافية لو سمحت، ما هو المتصفح المستخدم؟", 
            "الخطأ لا يظهر عندي في البيئة المحلية (Localhost)، هل يمكنك إرفاق صورة الشاشة؟", 
            "تم إصلاح الخلل وسيتم إدراجه في التحديث (Release) القادم.",
            "يبدو أن المشكلة في إعدادات السيرفر وليس في كود المصدر.", 
            "ممتاز، شكراً لك على الإبلاغ السريع.",
            "الرجاء محاولة مسح ملفات الارتباط (Cache) والمحاولة مرة أخرى.",
            "هذا ليس خطأ برمجي، بل هو متطلب جديد يجب إضافته كـ Feature Request."
        ]

        for issue in issues:
            # Create some comments
            if random.random() > 0.3:
                for _ in range(random.randint(1, 5)):
                    Comment.objects.create(
                        issue=issue,
                        user=random.choice(users),
                        content=random.choice(comment_texts)
                    )
                    
                    # backdate comments to be after issue created_at
                    last_comment = Comment.objects.last()
                    Comment.objects.filter(pk=last_comment.pk).update(
                        created_at=issue.created_at + timedelta(hours=random.randint(1, 48))
                    )
            
            # Create initial log
            IssueLog.objects.create(
                issue=issue,
                action="تم إنشاء التذكرة وإسنادها تلقائياً",
                new_value=issue.title,
                changed_by=issue.reported_by
            )
            IssueLog.objects.filter(pk=IssueLog.objects.last().pk).update(created_at=issue.created_at)
            
            # Create resolution log if resolved
            if issue.status in ['resolved', 'closed']:
                IssueLog.objects.create(
                    issue=issue,
                    action="تغيير الحالة إلى محلول",
                    old_value="قيد المعالجة",
                    new_value=issue.get_status_display(),
                    changed_by=issue.assigned_to or issue.reported_by
                )
                IssueLog.objects.filter(pk=IssueLog.objects.last().pk).update(created_at=issue.updated_at)

        self.stdout.write(self.style.SUCCESS('Successfully seeded the database with rich Arabic data!'))
