from argon2 import PasswordHasher

ph = PasswordHasher()

def verify_password(hashed, password):
    try:
        ph.verify(hashed, password)
        return True
    except:
        return False

def get_password_hash(password):
    return ph.hash(password)