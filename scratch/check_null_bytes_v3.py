import os

def check_file(path):
    try:
        with open(path, 'rb') as f:
            data = f.read()
            if b'\x00' in data:
                print(f"!!! NULL BYTES FOUND IN CODE FILE: {path}")
                return True
    except Exception as e:
        print(f"Error reading {path}: {e}")
    return False

def find_null_bytes(directory):
    found = []
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in ('venv', '.git', '.gemini', '__pycache__')]
        
        for file in files:
            if file.endswith(('.py', '.html', '.css', '.js', '.txt', '.pyw')):
                path = os.path.join(root, file)
                if check_file(path):
                    found.append(path)
    return found

if __name__ == "__main__":
    print("Starting search for null bytes in code files...")
    results = find_null_bytes(".")
    if not results:
        print("Done. No corrupted code files found in the project (excluding venv).")
    else:
        print(f"Done. Found {len(results)} corrupted code files.")
