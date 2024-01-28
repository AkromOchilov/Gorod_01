import hashlib

def hash_password(password):
    # Never store plain passwords; always hash them first
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def store_credentials(email, password):
    with open("users.txt", "a") as file:
        file.write(f"{email} {hash_password(password)}\n")

def verify_credentials(email, password):
    with open("users.txt", "r") as file:
        for line in file:
            stored_email, stored_hashed_password = line.strip().split()
            if stored_email == email and stored_hashed_password == hash_password(password):
                return True
    return False
