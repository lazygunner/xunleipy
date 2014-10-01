
def _md5(s):
    import hashlib
    return hashlib.md5(s.encode('utf-8')).hexdigest()

def get_password_hash(password, verify_code):
    return _md5(_md5(_md5(password)) + verify_code.upper())
