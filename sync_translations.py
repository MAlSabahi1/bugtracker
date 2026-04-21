import os
import re
import codecs
import subprocess

def get_all_html_files(directory):
    html_files = []
    for root, dirs, files in os.walk(directory):
        if 'venv' in root or 'sneat-' in root:
            continue
        for file in files:
            if file.endswith('.html'):
                html_files.append(os.path.join(root, file))
    return html_files

def extract_trans_strings(html_files):
    strings = set()
    trans_pattern = re.compile(r'\{% trans "([^"]+)" %\}')
    trans_pattern_single = re.compile(r"\{% trans '([^']+)' %\}")
    for file in html_files:
        with open(file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            strings.update(trans_pattern.findall(content))
            strings.update(trans_pattern_single.findall(content))
    return strings

def get_py_strings():
    import glob
    py_files = glob.glob("core/**/*.py", recursive=True)
    strings = set()
    pattern = re.compile(r'_\("([^"]+)"\)')
    for file in py_files:
        with open(file, 'r', encoding='utf-8', errors='ignore') as f:
            strings.update(pattern.findall(f.read()))
    return strings

missing_dictionary = {
    "Tracking Management": "إدارة وصلاحيات التتبع",
    "System Administration": "إدارة النظام المركزية",
    "Layouts": "القوالب",
    "Without menu": "بدون قائمة الجانبية",
    "Without navbar": "بدون الشريط العلوي",
    "Fluid": "مرن",
    "Container": "صندوقي",
    "Blank": "فارغ",
    "Account Settings": "إعدادات الحساب",
    "Account": "حسابي",
    "Notifications": "الإشعارات",
    "Connections": "الارتباطات",
    "Authentications": "المصادقة",
    "Login": "دخول",
    "Register": "تسجيل",
    "Forgot Password": "نسيت كلمة المرور",
    "Misc": "أخرى",
    "Error": "خطأ",
    "Under Maintenance": "تحت الصيانة",
    "Components": "المكونات",
    "Cards": "البطاقات",
    "User interface": "واجهات النظام",
    "Extended UI": "واجهات متقدمة",
    "Perfect scrollbar": "شريط التمرير",
    "Text Divider": "مقسم النصوص",
    "Boxicons": "أيقونات النظام",
    "Forms & Tables": "النماذج والجداول",
    "Form Elements": "عناصر النماذج",
    "Basic Inputs": "إدخال أساسي",
    "Input groups": "مجموعات الإدخال",
    "Form Layouts": "مخططات النماذج",
    "Vertical Form": "نموذج عمودي",
    "Horizontal Form": "نموذج أفقي",
    "Tables": "جدولة وتخطيط",
    "Documentation": "لوحة التوثيق",
    "Support": "الدعم والمساعدة",
    "App Screens": "شاشات المنظومة",
    "Manage": "إدارة شاملة",
    "Assign Screen": "سند شاشة للنظام",
    "Access Groups": "أذونات المجموعات",
    "All Permissions": "جميع سياسات التصريح",
    "Create Group": "صياغة مجمعة وصول",
    "Membership": "إدارة الأعضاء",
    "User Directory": "سجل الموظفين والمستفيدين",
    "Register User": "استقطاب وتسجيل موظف",
    "New Report": "رفع بلاغ جديد",
    "List All": "قائمة جميع السجلات",
    "Configure": "تهيئة واعداد البيانات",
    "Add New": "تسجيل بيئة جديدة",
    "Screens": "الشاشات",
    "Systems": "الأنظمة",
    "Screens Count": "إجمالي الشاشات",
    "Welcome to BugTracker! 👋": "أهلاً بك في نظام المتعقب! 👋",
    "Account is Active (Can Login)": "الاعتماد نشط (نعم/لا)",
    "Please fill in the technical details accurately": "يرجى تعبئة التفاصيل الفنية بدقة",
    "Core Information": "المعلومات الأساسية",
    "Technical Details & Context": "التفاصيل الفنية والسياق",
    "Assignment & Status": "الإسناد والحالة",
    "Resolution Data": "بيانات الحل",
    "Save Error Report": "حفظ بلاغ الخطأ",
    "Define and manage system properties": "تعريف وإدارة خصائص النظام",
    "Access & Permissions": "الوصول والصلاحيات",
    "Configure screen access and classification": "تهيئة وصول الشاشة وتصنيفها",
    "Group Access": "وصول المجموعات",
    "Manage team permissions and scope": "إدارة صلاحيات ونطاق الفريق",
    "Permissions Scope": "نطاق الصلاحيات",
    "User account settings and role management": "إعدادات حساب المستخدم وإدارة الأدوار",
    "Identity": "الهوية",
    "Access & Roles": "الوصول والأدوار",
    "Back to List": "العودة للقائمة",
    "Resolution details": "تفاصيل الحل",
    "Evidence / Attachment": "الدليل / المرفقات",
    "Discussion": "المناقشة",
    "No communication on this issue yet.": "لا يوجد تواصل بشأن هذا الخطأ بعد.",
    "Post Comment": "نشر تعليق",
    "Information": "المعلومات",
    "System": "النظام",
    "Screen": "الشاشة",
    "Assignee": "المسند إليه",
    "Target Team": "الفريق المستهدف",
    "Last Update": "آخر تحديث",
    "History Timeline": "سجل الأحداث",
    "Zero activity recorded.": "لم يتم تسجيل أي نشاط.",
    "Mark as Fixed": "تحديد كمصلح",
    "View Details": "عرض التفاصيل",
    "Cancel": "إلغاء",
    "Save System": "حفظ النظام",
    "Save Screen": "حفظ الشاشة",
    "Save Group": "حفظ المجموعة",
    "Save User": "حفظ المستخدم",
    "Systems Accessible": "الأنظمة المتاحة",
    "Specific Screens Assigned": "شاشات محددة مسندة",
    "My Dashboard": "لوحة التحكم الخاصة بي",
    "Select a system below to track its errors and operational progress.": "اختر نظاماً أدناه لتتبع أخطائه وسير العمليات فيه.",
    "My Systems": "أنظمتي",
    "No description provided.": "لا يوجد وصف متوفر.",
    "Enter Dashboard": "دخول لوحة التحكم",
    "No Operational Access": "لا يوجد صلاحية وصول عملياتية",
    "You are not currently assigned to any systems.": "أنت غير مسند لأي أنظمة حالياً.",
    "Your assigned systems represent the environments you are authorized to monitor.": "الأنظمة المسندة إليك تمثل البيئات التي لديك صلاحية مراقبتها.",
    "Excellent! Issue #%(id)s has been marked as Resolved.": "ممتاز! تم تحديد الخطأ رقم %(id)s كمحلول بنجاح.",
    "This report was auto-generated by the Bug Tracking System - OpenSoft Company": "تم توليد هذا التقرير تلقائياً بواسطة نظام تعقب الأخطاء - شركة أوبن سوفت",
    "Generate a complete report with no filters. Includes all systems, teams, and statuses.": "توليد تقرير كامل بدون فلاتر. يشمل جميع الأنظمة والفرق والحالات.",
    "This action will cascade and delete all associated screens, teams, issues, and comments. This is a highly destructive action.": "سيؤدي هذا الإجراء لحذف كافة الشاشات والفرق والأخطاء والتعليقات المرتبطة. هذا إجراء تدميري لا يمكن التراجع عنه.",
    "This action cannot be undone and will delete all associated comments and activity logs.": "هذا الإجراء نهائي وسيؤدي لحذف كافة التعليقات وسجلات النشاط المرتبطة.",
    "Generate, filter, and print official audit reports for all teams and systems.": "توليد وتصفية وطباعة تقارير التدقيق الرسمية لكافة الفرق والأنظمة.",
    "You are not authorized to resolve this issue.": "ليس لديك صلاحية لحل هذا الخطأ.",
    "The report opens in a new print-ready window. You can save it as PDF from the browser.": "سيفتح التقرير في نافذة جديدة جاهزة للطباعة. يمكنك حفظه كـ PDF من المتصفح.",
    "Please coordinate with your superior to obtain the necessary credentials.": "يرجى التنسيق مع مديرك المباشر للحصول على بيانات الاعتماد اللازمة.",
    "Note: Deleting a team will leave its members without a team assignment but will not delete the users.": "ملاحظة: حذف الفريق سيترك أعضاءه بدون فريق ولكن لن يحذف حسابات المستخدمين.",
    "Warning: Deleting a user will also delete all issues they reported and all comments they posted.": "تحذير: حذف المستخدم سيؤدي أيضاً لحذف كافة الأخطاء والتعليقات التي قام بنشرها.",
    "Quick Resolve": "حل سريع",
    "This issue is already resolved or closed.": "هذا الخطأ محلول أو مغلق بالفعل.",
    "There are currently no users registered in the system.": "لا يوجد مستخدمون مسجلون في النظام حالياً.",
    "We couldn't find any items matching your current view.": "لم نتمكن من العثور على أي عناصر تطابق العرض الحالي.",
    "Version": "الإصدار",
    "for stability": "لضمان الاستقرار",
    "to": "إلى",
    "Delete System": "حذف النظام",
    "Delete Screen": "حذف الشاشة",
    "Stakeholders": "المعنيون",
    "Systems Access": "الوصول للأنظمة",
    "Avatar": "الصورة الرمزية",
    "Recipient": "المستلم",
    "Message": "الرسالة",
    "Is Read": "تمت القراءة",
    "Other": "أخرى",
    "Delete Group": "حذف المجموعة",
    "Screenshot": "لقطة شاشة",
    "%(timesince)s ago": "منذ %(timesince)s",
    "This will delete all issues associated with this screen.": "سيؤدي هذا لحذف كافة الأخطاء المرتبطة بهذه الشاشة.",
    "Start by adding your first system to track errors and issues.": "ابدأ بإضافة نظامك الأول لتتبع الأخطاء والمشاكل.",
    "WELCOME": "مرحباً",
    "RASID": "راصد",
    "User Name": "اسم المستخدم",
    "Password": "كلمة المرور",
    "Forgot Password?": "نسيت كلمة المرور؟",
    "Sign in": "تسجيل الدخول",
    "Please sign in to access the monitoring dashboard.": "يرجى تسجيل الدخول للوصول إلى لوحة المتابعة.",
    "Rasid — A leading professional platform for bug tracking and software quality assurance. Provides a centralized system for monitoring application stability and managing security vulnerabilities through precise analytical reports.": "راصد — منصة احترافية رائدة لتتبع الأخطاء وضمان جودة البرمجيات. يوفر نظاماً مركزياً لمراقبة استقرار التطبيقات وإدارة الثغرات الأمنية من خلال تقارير تحليلية دقيقة.",
    "Good Morning": "صباح الخير",
    "Good Afternoon": "مساء الخير",
    "Good Evening": "مساء الخير",
    "Add New System": "إضافة نظام جديد",
    "Add New Group": "إضافة مجموعة جديدة",
    "Add New Screen": "إضافة شاشة جديدة",
    "Edit Error: %(title)s": "تعديل الخطأ: %(title)s",
    "Edit System: %(name)s": "تعديل النظام: %(name)s",
    "Edit Group: %(name)s": "تعديل المجموعة: %(name)s",
    "Edit Screen: %(name)s": "تعديل الشاشة: %(name)s",
    "Profile updated successfully.": "تم تحديث الملف الشخصي بنجاح.",
    "Password changed successfully.": "تم تغيير كلمة المرور بنجاح.",
    "Status Changed (Inline)": "تغيير الحالة (سريع)",
    "Comment Added": "تم إضافة تعليق",
    "Comment added successfully.": "تم إضافة التعليق بنجاح."
}

def main():
    po_file = 'locale/ar/LC_MESSAGES/django.po'
    
    html_files = get_all_html_files('.')
    trans_strings = extract_trans_strings(html_files)
    trans_strings.update(get_py_strings())
    
    print(f"Total unique translatable strings found in codebase: {len(trans_strings)}")
    
    with open(po_file, 'r', encoding='utf-8') as f:
        po_content = f.read()

    po_entries = set()
    for match in re.finditer(r'msgid "(.*?)"', po_content):
        po_entries.add(match.group(1))
        
    missing_in_po = trans_strings - po_entries
    print(f"Strings missing from django.po: {len(missing_in_po)}")
    
    # Append missing ones
    if missing_in_po:
        with open(po_file, 'a', encoding='utf-8') as f:
             f.write("\n")
             for s in missing_in_po:
                 val = missing_dictionary.get(s, s) # translate if possible else keep same
                 f.write(f'msgid "{s}"\n')
                 f.write(f'msgstr "{val}"\n\n')
                 
    # Now load translation dict 
    all_dict = {}
    all_dict.update(missing_dictionary)

    # Let's do a direct sweep to translate ALL strings in django.po whether empty or not, 
    # to guarantee 100% Arabic mappings.
    with open(po_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    out_lines = []
    current_msgid = ""
    for line in lines:
        if line.startswith("msgid "):
            current_msgid = re.search(r'msgid "(.*)"', line).group(1) if re.search(r'msgid "(.*)"', line) else ""
            out_lines.append(line)
        elif line.startswith('msgstr "'):
            if current_msgid and current_msgid in all_dict:
                out_lines.append(f'msgstr "{all_dict[current_msgid]}"\n')
            else:
                out_lines.append(line)
            current_msgid = ""
        else:
            out_lines.append(line)
            
    with open(po_file, "w", encoding="utf-8") as f:
        f.writelines(out_lines)
        
    print("Auto-injection complete!")
    
    # Finally compile the messages to MO file!
    try:
        subprocess.check_call(["python", "manage.py", "compilemessages", "-l", "ar"])
        print("Compiled successfully!")
    except Exception as e:
        print("Compile failed:", str(e))

if __name__ == "__main__":
    main()
