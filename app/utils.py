import hashlib

# Hash the password directly without salt
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

# Check if the entered password matches the stored hash
def check_password(stored_hash: str, password: str) -> bool:
    return stored_hash == hashlib.sha256(password.encode('utf-8')).hexdigest()
