import re

file_path = r'c:\Users\alsabahi\Documents\bugtracker\locale\ar\LC_MESSAGES\django.po'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Truncate any manually appended block at the end that causes duplicates
# We detect the start of the 'corrupt' section
corrupt_start = content.find('\n\nmsgid "Bug Tracking & Security Testing System')
if corrupt_start != -1:
    content = content[:corrupt_start]

# Explicit replacements for the core terms in their source-linked blocks
replacements = {
    'msgstr "خطوات التكرار..."': 'msgstr "كيف حدثت المشكلة؟..."',
    'msgstr "خطوات التكرار"': 'msgstr "كيف حدثت المشكلة؟"',
    'msgstr "النتيجة الفعلية..."': 'msgstr "ماذا حدث بالضبط؟ (الخطأ الحالي)..."',
    'msgstr "النتيجة الفعلية"': 'msgstr "ماذا حدث بالضبط؟ (الخطأ الحالي)"',
    'msgstr "النتيجة المتوقعة..."': 'msgstr "ماذا كان يجب أن يحدث؟ (السلوك الصحيح)..."',
    'msgstr "النتيجة المتوقعة"': 'msgstr "ماذا كان يجب أن يحدث؟ (السلوك الصحيح)"',
    
    # Dashboard items (might be fuzzy or empty after makemessages)
    'msgid "Resolved for Review"\nmsgstr ""': 'msgid "Resolved for Review"\nmsgstr "بلاغات تنتظر المراجعة والإغلاق"',
    'msgid "Audit & Close"\nmsgstr ""': 'msgid "Audit & Close"\nmsgstr "تعميد وإغلاق"',
    'msgid "Tasks Pending"\nmsgstr ""': 'msgid "Tasks Pending"\nmsgstr "بلاغات قيد المراجعة"',
    'msgid "Verification queue for finalized engineering tasks"\nmsgstr ""': 'msgid "Verification queue for finalized engineering tasks"\nmsgstr "قائمة التحقق للمهام البرمجية المكتملة"',
}

for old, new in replacements.items():
    content = content.replace(old, new)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("PO File Surgical Sanitization Complete.")
