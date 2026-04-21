import os

po_file = r'c:\Users\alsabahi\Documents\bugtracker\locale\ar\LC_MESSAGES\django.po'

new_translations = """
#: templates/core/dashboard.html:38
msgid "Welcome back to your operational control center."
msgstr "مرحباً بك مجدداً في مركز التحكم والعمليات الخاص بك."

#: templates/core/dashboard.html:46
msgid "Errors Found"
msgstr "أخطاء مكتشفة"

#: templates/core/dashboard.html:50
msgid "Resolved"
msgstr "تم حلها"

#: templates/core/dashboard.html:54
msgid "Growth"
msgstr "نمو"

#: templates/core/dashboard.html:73
msgid "Your recent activity is highly efficient: <strong>%(total)s critical errors</strong> have been successfully resolved in the last 24 hours."
msgstr "نشاطك الأخير فعال للغاية: تم حل <strong>%(total)s أخطاء حرجة</strong> بنجاح خلال الـ 24 ساعة الماضية."

#: templates/core/dashboard.html:75
msgid "Immediate attention required: <strong>%(open)s pending errors</strong> are currently awaiting audit."
msgstr "انتباه فوري مطلوب: هناك <strong>%(open)s أخطاء معلقة</strong> بانتظار المراجعة حالياً."

#: templates/core/dashboard.html:82
msgid "Error Tracking"
msgstr "تتبع الأخطاء"

#: templates/core/dashboard.html:85
msgid "New Error"
msgstr "خطأ جديد"

#: templates/layout/partials/empty_state.html:3
msgid "No results found"
msgstr "لم يتم العثور على نتائج"

#: templates/layout/partials/empty_state.html:4
msgid "We couldn't find any items matching your current view."
msgstr "لم نتمكن من العثور على أي عناصر تطابق عرضك الحالي."

#: templates/layout/partials/empty_state.html:6
msgid "Add New"
msgstr "إضافة جديد"

#: templates/core/users/user_list.html
msgid "No users found"
msgstr "لم يتم العثور على مستخدمين"

#: templates/core/users/user_list.html
msgid "There are currently no users registered in the system."
msgstr "لا يوجد مستخدمون مسجلون في النظام حالياً."

#: templates/core/users/user_list.html
msgid "Add First User"
msgstr "إضافة أول مستخدم"

#: templates/core/systems/system_list.html
msgid "No systems defined"
msgstr "لا توجد أنظمة معرفة"

#: templates/core/systems/system_list.html
msgid "Start by adding your first system to track errors and issues."
msgstr "ابدأ بإضافة أول نظام لك لتتبع الأخطاء والمشكلات."

#: templates/core/systems/system_list.html
msgid "Create System"
msgstr "إنشاء نظام"

#: templates/core/issues/issue_list.html
msgid "No errors tracked"
msgstr "لا توجد أخطاء متتبعة"

#: templates/core/issues/issue_list.html
msgid "No issues match your current filters or there are no reports in the system."
msgstr "لا توجد أخطاء تطابق فلاتر البحث الحالية أو لا توجد تقارير في النظام."

#: templates/core/issues/issue_list.html
msgid "Report New Error"
msgstr "إبلاغ عن خطأ جديد"
"""

with open(po_file, 'a', encoding='utf-8') as f:
    f.write(new_translations)

print("Translations appended successfully.")
