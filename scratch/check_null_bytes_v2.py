import os

def check_file(path):
    try:
        with open(path, 'rb') as f:
            data = f.read()
            if b'\x00' in data:
                print(f"!!! NULL BYTES FOUND: {path}")
                return True
    except Exception as e:
        print(f"Error reading {path}: {e}")
    return False

def find_null_bytes(directory):
    found = []
    for root, dirs, files in os.walk(directory):
        # Explicitly skip venv/etc
        dirs[:] = [d for d in dirs if d not in ('venv', '.git', '.gemini', '__pycache__')]
        
        for file in files:
            path = os.path.join(root, file)
            if check_file(path):
                found.append(path)
    return found

if __name__ == "__main__":
    print("Starting search for null bytes...")
    results = find_null_bytes(".")
    if not results:
        print("Done. No corrupted files found in the project (excluding venv).")
    else:
        print(f"Done. Found {len(results)} corrupted files.")
