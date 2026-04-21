import re
import os

def check_translations():
    po_file = 'locale/ar/LC_MESSAGES/django.po'
    if not os.path.exists(po_file):
        print("PO file not found")
        return

    with open(po_file, 'r', encoding='utf-8') as f:
        content = f.read()

    targets = [
        "Manage team permissions and scope",
        "Permissions Scope",
        "Identity",
        "Access & Roles",
        "Core Information",
        "Technical Details & Context",
        "Assignment & Status",
        "Resolution Data",
        "Save Error Report",
        "Define and manage system properties"
    ]

    for t in targets:
        # Search for msgid and the following msgstr
        pattern = r'msgid "' + re.escape(t) + r'"\nmsgstr "(.*?)"'
        match = re.search(pattern, content)
        if match:
            print(f"ID: {t} -> STR: {match.group(1)}")
        else:
            print(f"ID: {t} -> NOT FOUND")

if __name__ == "__main__":
    check_translations()
