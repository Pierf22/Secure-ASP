import bcrypt


def verify_password(plain_password, hashed_password):
    password_bytes_encoded = plain_password.encode("utf-8")
    hashed_password_bytes_encoded = hashed_password.encode("utf-8")
    return bcrypt.checkpw(password_bytes_encoded, hashed_password_bytes_encoded)


def get_password_hash(password: str):
    salt = bcrypt.gensalt()
    pwd_bytes = password.encode("utf-8")
    return bcrypt.hashpw(pwd_bytes, salt)
