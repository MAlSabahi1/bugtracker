import os
import re

def fix_po_duplicates(po_file_path):
    if not os.path.exists(po_file_path):
        print(f"File not found: {po_file_path}")
        return

    with open(po_file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Pattern to match msgid and msgstr pairs
    # Note: this is a simple pattern, might need refinement for multiline strings
    blocks = re.findall(r'(msgid ".*?"\nmsgstr ".*?"\n)', content, re.DOTALL)
    
    seen_ids = set()
    unique_blocks = []
    
    # We want to keep the header (usually before the first msgid)
    header = content.split('msgid ""')[0] if 'msgid ""' in content else ""
    if header:
        # Check if the empty msgid (header) is in blocks
        header_block = re.search(r'(msgid ""\nmsgstr ".*?"\n)', content, re.DOTALL)
        if header_block:
             seen_ids.add("")
             unique_blocks.append(header_block.group(1))

    # Re-parse to find all blocks including multiline
    # A block starts with optional comments, then msgid, then msgstr
    all_blocks = re.split(r'\n(?=#|msgid)', content)
    
    final_output = []
    for block in all_blocks:
        msgid_match = re.search(r'msgid "(.*)"', block)
        if msgid_match:
            msgid = msgid_match.group(1)
            if msgid not in seen_ids:
                seen_ids.add(msgid)
                final_output.append(block)
        else:
            # If it doesn't have a msgid, it might be the header or comments at top
            if not final_output:
                final_output.append(block)

    with open(po_file_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(final_output))

    print(f"Duplicates removed. Unique strings: {len(seen_ids)}")

if __name__ == "__main__":
    fix_po_duplicates('locale/ar/LC_MESSAGES/django.po')
