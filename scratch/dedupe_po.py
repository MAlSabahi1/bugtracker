import re

def deduplicate_po(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split by double newline to get entries
    # But wait, comments can be connected to entries.
    # Better to split by lines and gather.
    lines = content.splitlines()
    
    header = []
    entries = []
    current_comments = []
    current_msgid = None
    current_msgstr = None
    
    in_msgid = False
    in_msgstr = False
    
    has_seen_msgid_header = False

    for line in lines:
        if not has_seen_msgid_header:
            if line.startswith('msgid ""'):
                has_seen_msgid_header = True
                in_msgid = True
                current_msgid = ""
                # Treat the header start as a normal entry start
            else:
                header.append(line + "\n")
                continue

        if line.startswith('#'):
            if current_msgid is not None:
                entries.append({'comments': current_comments, 'msgid': current_msgid, 'msgstr': current_msgstr})
                current_comments = []
                current_msgid = None
                current_msgstr = None
            current_comments.append(line + "\n")
            in_msgid = False
            in_msgstr = False
        elif line.startswith('msgid'):
            if current_msgid is not None and not in_msgid: # New entry without starting comment
                 entries.append({'comments': current_comments, 'msgid': current_msgid, 'msgstr': current_msgstr})
                 current_comments = []
            
            match = re.search(r'msgid "(.*)"', line)
            if match:
                current_msgid = match.group(1)
            else:
                current_msgid = ""
            in_msgid = True
            in_msgstr = False
        elif line.startswith('msgstr'):
            match = re.search(r'msgstr "(.*)"', line)
            if match:
                current_msgstr = match.group(1)
            else:
                current_msgstr = ""
            in_msgid = False
            in_msgstr = True
        elif line.startswith('"'):
            match = re.search(r'"(.*)"', line)
            if match:
                if in_msgid:
                    current_msgid += match.group(1)
                elif in_msgstr:
                    current_msgstr += match.group(1)
        elif not line.strip():
            if current_msgid is not None:
                entries.append({'comments': current_comments, 'msgid': current_msgid, 'msgstr': current_msgstr})
                current_comments = []
                current_msgid = None
                current_msgstr = None
            in_msgid = False
            in_msgstr = False

    if current_msgid is not None:
        entries.append({'comments': current_comments, 'msgid': current_msgid, 'msgstr': current_msgstr})

    # Deduplicate
    seen = {}
    unique_entries = []
    for e in entries:
        mid = e['msgid']
        if mid not in seen:
            seen[mid] = e
            unique_entries.append(e)
        else:
            # Upgrade translation if duplicate has one
            if e['msgstr'] and not seen[mid]['msgstr']:
                seen[mid]['msgstr'] = e['msgstr']
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(header)
        for e in unique_entries:
            f.writelines(e['comments'])
            f.write(f'msgid "{e["msgid"]}"\n')
            f.write(f'msgstr "{e["msgstr"]}"\n\n')

if __name__ == "__main__":
    deduplicate_po(r'c:\Users\alsabahi\Documents\bugtracker\locale\ar\LC_MESSAGES\django.po')
    print("PO file deduplicated successfully.")
