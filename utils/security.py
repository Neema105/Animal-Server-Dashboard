import hashlib


HASH_PREFIX = "sha256$"


def hash_password(password: str) -> str:
    password = password or ""
    return f"{HASH_PREFIX}{hashlib.sha256(password.encode('utf-8')).hexdigest()}"


def is_hashed_password(password: str) -> bool:
    return isinstance(password, str) and password.startswith(HASH_PREFIX)


def verify_password(password: str, stored_password: str) -> bool:
    if not stored_password:
        return False
    if is_hashed_password(stored_password):
        return stored_password == hash_password(password)
    return stored_password == (password or "")
