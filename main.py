import hashlib
import json
import os


def hash_file(filepath):
    """Calculates the cryptographic hash (SHA-256) of a file's contents."""
    hasher = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return None


def traverse_directory(dir_path):
    """Navigates to the directory and builds a mapping of files and hashes."""
    file_hashes = {}
    if not os.path.exists(dir_path):
        print(f"Directory '{dir_path}' does not exist.")
        return None

    for root, _, files in os.walk(dir_path):
        for file in files:
            if file == "hashes.json":
                continue
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, dir_path)
            file_hash = hash_file(full_path)
            if file_hash:
                file_hashes[rel_path] = file_hash

    return file_hashes


def generate_table(dir_path):
    """Generates and saves the hashes.json table."""
    file_hashes = traverse_directory(dir_path)
    if file_hashes is None:
        return

    json_path = os.path.join(dir_path, "hashes.json")
    with open(json_path, "w") as f:
        json.dump(file_hashes, f, indent=4)

    print("Hash table generated")


def validate_hash(dir_path):
    """Verifies existing files, detects modifications, additions, deletions, and renames (Bonus)."""
    json_path = os.path.join(dir_path, "hashes.json")
    if not os.path.exists(json_path):
        print("Error: 'hashes.json' not found in this directory.")
        return

    with open(json_path, "r") as f:
        stored_hashes = json.load(f)

    current_hashes = traverse_directory(dir_path)
    if current_hashes is None:
        return

    stored_hash_to_path = {
        h: path for path, h in stored_hashes.items() if h is not None
    }
    updated_hashes = dict(stored_hashes)
    table_modified = False

    for rel_path, curr_hash in current_hashes.items():
        if rel_path in stored_hashes:
            if stored_hashes[rel_path] == curr_hash:
                print(f"{rel_path} hash is valid")
            else:
                print(f"{rel_path} hash is invalid")
        else:
            if curr_hash in stored_hash_to_path:
                old_rel_path = stored_hash_to_path[curr_hash]
                print(
                    f"File name change detected, {old_rel_path} has been renamed to {rel_path}"
                )
                del updated_hashes[old_rel_path]
                updated_hashes[rel_path] = curr_hash
                table_modified = True
            else:
                print(f"New file added: {rel_path}")

    for old_path in stored_hashes:
        if (
            old_path not in current_hashes
            and old_path not in updated_hashes.values()
        ):
            if old_path not in [
                stored_hash_to_path.get(h)
                for h in current_hashes.values()
                if h in stored_hash_to_path
            ]:
                print(f"File deleted: {old_path}")

    if table_modified:
        with open(json_path, "w") as f:
            json.dump(updated_hashes, f, indent=4)


def main():
    print("Select an option:")
    print("1. Generate a new hash table")
    print("2. Verify hashes")
    choice = input("Enter choice (1 or 2): ").strip()

    dir_path = input("Enter the directory path: ").strip()

    if choice == "1":
        generate_table(dir_path)
    elif choice == "2":
        validate_hash(dir_path)
    else:
        print("Invalid option selected.")


if __name__ == "__main__":
    main()