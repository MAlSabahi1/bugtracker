import re
from collections import Counter

def check_po(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Simple regex to find msgid entries
    ids = re.findall(r'^msgid "(.*)"', content, re.MULTILINE)
    
    counts = Counter(ids)
    duplicates = {k: v for k, v in counts.items() if v > 1 and k != ""}
    
    if duplicates:
        print("Duplicates found:")
        for k, v in duplicates.items():
            print(f"  '{k}': {v} times")
    else:
        print("No duplicates found.")

    # Check for empty msgstr for existing msgids
    # This might help identify what needs translation
    # (But we mostly care about duplicates for compile errors)

if __name__ == "__main__":
    check_po(r'c:\Users\alsabahi\Documents\bugtracker\locale\ar\LC_MESSAGES\django.po')
