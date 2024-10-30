class UsuariosDTO:
    def __init__(self, id, username, password, created_at):
        self.id = id
        self.username = username
        self.password = password
        self.created_at = created_at

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "password": self.password,
            "created_at": self.created_at
        }
