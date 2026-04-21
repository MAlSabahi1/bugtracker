import os

def clean_po_file(po_file_path):
    if not os.path.exists(po_file_path):
        return

    with open(po_file_path, 'r', encoding='utf-8-sig') as f:
        lines = f.readlines()

    clean_lines = []
    skip_obsolete = True
    
    for line in lines:
        # Remove obsolete lines (starting with #~)
        if line.startswith('#~'):
            continue
        
        # Remove fuzzy markers (optional, but good for forcing translations)
        if line.startswith('#, fuzzy'):
            continue
            
        clean_lines.append(line)

    # Further check: ensure every msgid has a msgstr
    final_lines = []
    i = 0
    while i < len(clean_lines):
        line = clean_lines[i]
        if line.startswith('msgid "'):
            # Look ahead for msgstr
            has_msgstr = False
            for j in range(i+1, min(i+5, len(clean_lines))):
                if clean_lines[j].startswith('msgstr "'):
                    has_msgstr = True
                    break
                if clean_lines[j].startswith('msgid "'):
                    break # Found next msgid without msgstr
            
            if has_msgstr:
                final_lines.append(line)
            else:
                print(f"Warning: stripping msgid without msgstr: {line.strip()}")
                # Skip this msgid
                i += 1
                continue
        else:
            final_lines.append(line)
        i += 1

    with open(po_file_path, 'w', encoding='utf-8-sig') as f:
        f.writelines(final_lines)

    print("PO file cleaned of obsolete and broken entries.")

if __name__ == "__main__":
    clean_po_file('locale/ar/LC_MESSAGES/django.po')
