import re

def clean_po(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Define the correct translations
    translations = {
        'Groups List': 'قائمة المجموعات',
        'Systems List': 'قائمة الأنظمة',
        'Screens List': 'قائمة الشاشات',
        'Users List': 'قائمة المستخدمين',
        'Add Issue': 'إضافة بلاغ',
        'Add System': 'إضافة نظام',
        'Add Screen': 'إضافة شاشة',
        'Add Group': 'إضافة مجموعة',
        'Add User': 'إضافة مستخدم',
        'BugTracker': 'متتبع الأخطاء',
    }

    # 1. Remove fuzzy tags for THESE specific ids
    for msgid, msgstr in translations.items():
        # Find the block containing the fuzzy tag and the msgid
        # Regex to find a fuzzy tag followed by optional lines/comments and then the specific msgid
        pattern = re.compile(f'#, fuzzy\n(#.*\n)*msgid "{re.escape(msgid)}"', re.MULTILINE)
        if pattern.search(content):
            content = pattern.sub(f'msgid "{msgid}"', content)
            print(f"Removed fuzzy tag for: {msgid}")

        # 2. Update the msgstr if it's incorrect or empty
        # This regex matches the msgid and the AFTER msgstr
        pattern_str = re.compile(f'(msgid "{re.escape(msgid)}"\n)msgstr ".*?"', re.MULTILINE)
        if pattern_str.search(content):
            content = pattern_str.sub(r'\1msgstr "' + msgstr + '"', content)
            print(f"Updated msgstr for: {msgid}")

    # 3. Aggressive cleanup for ALL fuzzy tags that have a translation (optional but safe here)
    # Actually, let's just stick to the specific ones to avoid breaking other things.

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == "__main__":
    clean_po(r'c:\Users\alsabahi\Documents\bugtracker\locale\ar\LC_MESSAGES\django.po')
    print("PO file cleaned successfully.")
