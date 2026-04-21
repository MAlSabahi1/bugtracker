import os

def restore_po_header(po_file_path):
    header = r'''msgid ""
msgstr ""
"Project-Id-Version: PACKAGE VERSION\n"
"Report-Msgid-Bugs-To: \n"
"POT-Creation-Date: 2026-04-21 12:00+0000\n"
"PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE\n"
"Last-Translator: FULL NAME <EMAIL@ADDRESS>\n"
"Language-Team: LANGUAGE <LL@li.org>\n"
"Language: ar\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=UTF-8\n"
"Content-Transfer-Encoding: 8bit\n"
"Plural-Forms: nplurals=6; plural=n==0 ? 0 : n==1 ? 1 : n==2 ? 2 : n%100>=3 && n%100<=10 ? 3 : n%100>=11 && n%100<=99 ? 4 : 5;\n"

'''
    if not os.path.exists(po_file_path):
        return

    with open(po_file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if header already exists
    if 'Content-Type: text/plain; charset=UTF-8' in content:
        print("Header seems to exist.")
        # But maybe it's not at the very top. Let's fix it anyway.
    
    # Remove any existing empty msgid header if it's broken
    content = content.replace('msgid ""\nmsgstr ""', "")
    
    # Clean up content to remove other headers if any
    # (Simple approach: keep only non-empty msgid blocks)
    
    with open(po_file_path, 'w', encoding='utf-8') as f:
        f.write(header + content)

    print("Header restored.")

if __name__ == "__main__":
    restore_po_header('locale/ar/LC_MESSAGES/django.po')
