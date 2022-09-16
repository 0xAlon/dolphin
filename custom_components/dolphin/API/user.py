class User(object):
    access_key: str
    email: str

    def __init__(self, access_key: str = None, email: str = None):
        self.access_key = access_key if access_key else None
        self.email = email if email else None
