import os

po_file = r'c:\Users\alsabahi\Documents\bugtracker\locale\ar\LC_MESSAGES\django.po'

# Remove the previous attempt if it didn't work well or needs replacement
# In this case, I'll just append the specific growth translation

new_translations = """
#: templates/core/dashboard.html:54
msgid "%(growth)s%% Growth"
msgstr "نمو بنسبة %(growth)s%%"
"""

with open(po_file, 'a', encoding='utf-8') as f:
    f.write(new_translations)

print("Growth translation appended successfully.")
