import codecs
import os

# Standardized Arabic Dictionary for Bug Tracker (Standard UI Defaults)
dictionary = {
    # Sidebar & Menu (Standardized)
    "Dashboard": "لوحة التحكم",
    "Tracking Management": "إدارة المشاكل",
    "Fault Registry": "سجل المشاكل",
    "List All": "قائمة الكل",
    "New Report": "إضافة بلاغ",
    "System Administration": "إدارة النظام",
    "Systems": "الأنظمة",
    "Configure": "الإعدادات",
    "Add New": "إضافة جديد",
    "App Screens": "شاشات النظام",
    "Manage": "إدارة",
    "Assign Screen": "ربط شاشة",
    "Access Groups": "مجموعات الصلاحيات",
    "All Permissions": "كافة الصلاحيات",
    "Create Group": "إضافة مجموعة",
    "Membership": "المستخدمين",
    "User Directory": "قائمة المستخدمين",
    "Register User": "إضافة مستخدم",
    
    # Common Headers
    "Name": "الاسم",
    "Description": "الوصف",
    "Status": "الحالة",
    "Issues": "المشاكل",
    "Screens": "الشاشات",
    "Actions": "الإجراءات",
    "Role": "الصلاحية",
    "User": "المستخدم",
    "Date": "التاريخ",
    "Title": "العنوان",
    "Priority": "الأولوية",
    "System": "النظام",
    "Screen": "الشاشة",
    
    # Dashboards
    "Welcome back": "مرحباً بك",
    "Critical": "حرج",
    "High": "عالي",
    "Medium": "متوسط",
    "Low": "منخفض",
    "Open": "مفتوح",
    "In Progress": "قيد المعالجة",
    "Resolved": "تم الحل",
    "Closed": "مغلق",
    "Reopened": "أعيد فتحه",
    "High Priority": "أولوية عالية",
    "Recent Issues": "أحدث المشاكل",
    "View All": "عرض الكل",
    "Report Bug": "إبلاغ عن مشكلة",
    "Fixed": "تم الإصلاح",
    "Total Bugs": "إجمالي الأعطال",
    "Top Performers": "الأكثر إنجازاً",
    "System Activity Log": "سجل النشاط",
    "Tasks": "المهام",
    
    # Models & Fields
    "Is Active": "نشط",
    "Groups": "المجموعات",
    "Comment": "تعليق",
    "Comments": "التعليقات",
    "Issue": "مشكلة",
    "Reported By": "بواسطة",
    "Assigned To": "المُسند إليه",
    "Issue Type": "نوع المشكلة",
    "Target Team": "الفريق المختص",
    "Steps to Reproduce": "خطوات التكرار",
    "Expected Result": "النتيجة المتوقعة",
    "Actual Result": "النتيجة الفعلية",
    "Created At": "تاريخ الإنشاء",
    "Updated At": "تاريخ التحديث",
    "Action": "العملية",
    "Old Value": "القيمة السابقة",
    "New Value": "القيمة الجديدة",
    "Changed By": "تعديل بواسطة",
    
    # Form Labels & Placeholders
    "Username": "اسم المستخدم",
    "Enter your username": "أدخل اسم المستخدم",
    "Password": "كلمة المرور",
    "Email": "البريد الإلكتروني",
    "Full Name": "الاسم الكامل",
    "First Name": "الاسم الأول",
    "Last Name": "الاسم الأخير",
    "User Role": "صلاحية المستخدم",
    "Groups Assignment": "تعيين المجموعات",
    "Account is Active (Can Login)": "الحساب نشط",
    "Required for new users.": "مطلوب للمستخدمين الجدد",
    "Issue title": "عنوان المشكلة",
    "Describe the issue...": "وصف المشكلة...",
    "Steps to reproduce...": "خطوات التكرار...",
    "Expected result...": "النتيجة المتوقعة...",
    "Actual result...": "النتيجة الفعلية...",
    "All Statuses": "كل الحالات",
    "All Priorities": "كل الأولويات",
    "All Types": "كل الأنواع",
    "Search issues...": "بحث...",
    "Write a comment...": "اكتب تعليقاً...",
    "System name": "اسم النظام",
    "System description...": "وصف النظام...",
    "Screen name": "اسم الشاشة",
    "Group name": "اسم المجموعة",
    "Team Name": "اسم الفريق",
    "Team Leader": "رئيس الفريق",
    
    # Buttons & Actions
    "Save": "حفظ",
    "Cancel": "إلغاء",
    "Edit": "تعديل",
    "Delete": "حذف",
    "Back to List": "رجوع",
    "Save Issue": "حفظ المشكلة",
    "Save User": "حفظ المستخدم",
    "Save System": "حفظ النظام",
    "Save Screen": "حفظ الشاشة",
    "Save Group": "حفظ المجموعة",
    "Save Team": "حفظ الفريق",
    "Confirm Delete": "تأكيد الحذف",
    "Add System": "إضافة نظام",
    "Add User": "إضافة مستخدم",
    "Add Screen": "إضافة شاشة",
    "Add Group": "إضافة مجموعة",
    "Add Team": "إضافة فريق",
    "Add New System": "إضافة نظام جديد",
    "Add New Group": "إضافة مجموعة جديدة",
    "Add New Screen": "إضافة شاشة جديدة",
    "Add New User": "إضافة مستخدم جديد",
    "Create User": "إنشاء مستخدم",
    
    # Auth
    "Login": "دخول",
    "Remember Me": "تذكرني",
    "Forgot Password?": "نسيت كلمة المرور؟",
    "New on our platform?": "جديد؟",
    "Create an account": "إنشاء حساب",
    "Sign in": "تسجيل الدخول",
    "Welcome to": "مرحباً بك في",
    "Please sign-in to your account and start the adventure": "الرجاء تسجيل الدخول للمتابعة",
    
    # Generic
    "Inactive": "غير نشط",
    "Active": "نشط",
    "No systems defined yet.": "لا يوجد أنظمة.",
    "No activities recorded.": "لا يوجد أنشطة.",
    "No activity recorded.": "لا يوجد أنشطة.",
    "No issues found matching your criteria.": "لا يوجد نتائج.",
    "No users found in the system.": "لا يوجد مستخدمين.",
    "Search...": "بحث...",
    "My Profile": "ملفي الشخصي",
    "Settings": "الإعدادات",
    "Log Out": "خروج",
    "Systems Directory": "سجل الأنظمة",
    "User Management": "إدارة المستخدمين",
    "Screens Management": "إدارة الشاشات",
    "Group Access Management": "إدارة الصلاحيات",
    "Permission Group Profile": "بيانات المجموعة",
    "Accessible Systems": "الأنظمة المتاحة",
    "Assigned Groups": "المجموعات المعينة",
    "Assigned Screens": "الشاشات المعينة",
    "Member Count": "الأعضاء",
    "Delete User": "حذف المستخدم",
    "Edit User: %(username)s": "تعديل المستخدم: %(username)s",
    "Edit Issue: %(title)s": "تعديل المشكلة: %(title)s",
    "Edit System: %(name)s": "تعديل النظام: %(name)s",
    "Edit Screen: %(name)s": "تعديل الشاشة: %(name)s",
    "Edit Group: %(name)s": "تعديل المجموعة: %(name)s",
}

def translate_po(file_path):
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return

    with codecs.open(file_path, "r", "utf-8") as f:
        content = f.read()

    content = content.replace('\r\n', '\n')
    lines = content.split('\n')

    new_lines = []
    current_id = None
    
    for line in lines:
        stripped = line.strip()
        
        if stripped.startswith('msgid "'):
            current_id = stripped[7:-1]
            new_lines.append(line)
        elif stripped.startswith('msgstr "'):
            if current_id and current_id in dictionary:
                new_lines.append(f'msgstr "{dictionary[current_id]}"')
            elif current_id and current_id.capitalize() in dictionary:
                 new_lines.append(f'msgstr "{dictionary[current_id.capitalize()]}"')
            else:
                new_lines.append(line)
            current_id = None
        else:
            new_lines.append(line)

    with codecs.open(file_path, "w", "utf-8") as f:
        f.write('\n'.join(new_lines))
    print(f"Standardized dictionary applied to {file_path}")

if __name__ == "__main__":
    translate_po("locale/ar/LC_MESSAGES/django.po")
