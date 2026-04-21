import os

def debug_long_string():
    po_file = 'locale/ar/LC_MESSAGES/django.po'
    html_file = 'templates/core/auth/login.html'
    
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Extract string from HTML (manual search for line 455 area)
    # Search for the pattern {% trans "..." %}
    import re
    matches = re.findall(r'\{% trans "(Rasid —.*?)" %\}', html_content)
    if not matches:
        print("Could not find string in HTML")
        return
    
    html_str = matches[0]
    print(f"String in HTML: '{html_str}' (Length: {len(html_str)})")
    
    with open(po_file, 'r', encoding='utf-8') as f:
        po_content = f.read()
    
    # Check for direct match in PO
    if f'msgid "{html_str}"' in po_content:
        print("EXACT MATCH found in PO file.")
        # Find msgstr
        pattern = r'msgid "' + re.escape(html_str) + r'"\nmsgstr "(.*?)"'
        match = re.search(pattern, po_content)
        if match:
            print(f"Translation: {match.group(1)}")
        else:
            print("Translation (msgstr) NOT found!")
    else:
        print("NO MATCH in PO file!")
        # Let's see what's in PO starting with Rasid
        match = re.search(r'msgid "(Rasid.*?)"', po_content)
        if match:
            print(f"Closest PO string: '{match.group(1)}' (Length: {len(match.group(1))})")
            # Compare char by char
            s1 = html_str
            s2 = match.group(1)
            for i in range(min(len(s1), len(s2))):
                if s1[i] != s2[i]:
                    print(f"Mismatch at index {i}: '{s1[i]}' vs '{s2[i]}'")
                    break
        else:
            print("No string starting with 'Rasid' found in PO.")

if __name__ == "__main__":
    debug_long_string()
