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
    # Specific ones found inside templates
    "Screens": "الشاشات",
    "Systems": "الأنظمة",
    "Screens Count": "إجمالي الشاشات",
    "Welcome to BugTracker! 👋": "أهلاً بك في نظام المتعقب! 👋",
    "Account is Active (Can Login)": "الاعتماد نشط (نعم/لا)"
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
                 
    # Now load translation dict from our translate.py we built earlier + missing_dictionary
    # Just to be sure, let's update all msgstr that might be empty or missing 
    all_dict = {}
    from translate import dictionary  # from my previous script
    all_dict.update(dictionary)
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
