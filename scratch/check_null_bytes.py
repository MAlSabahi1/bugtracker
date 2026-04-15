import os

def find_null_bytes(directory):
    for root, dirs, files in os.walk(directory):
        if 'venv' in dirs:
            dirs.remove('venv')  # Skip virtualenv
        if '.git' in dirs:
            dirs.remove('.git')
        
        for file in files:
            if file.endswith(('.py', '.html', '.css', '.js')):
                path = os.path.join(root, file)
                try:
                    with open(path, 'rb') as f:
                        if b'\x00' in f.read():
                            print(f"NULL BYTES FOUND: {path}")
                except Exception as e:
                    print(f"Error reading {path}: {e}")

if __name__ == "__main__":
    find_null_bytes(".")
