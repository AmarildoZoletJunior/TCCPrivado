import re
import bcrypt

from src.data.database import Database
from src.entidades.usuarios import Usuarios


class UserRepository:
    def __init__(self, Data):
        self.Data = Data
        self.pattern = r"^(?=.*[0-9])(?=.*[!@#$%^&*(),.?\":{}|<>])(?=.*[A-Z])(?=.*[a-z]).+$"
        self.login = None
        self.password = None


    def hash_senha(self, senha):
        return bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def verificar_senha(self, senha, hash_armazenado):
        return bcrypt.checkpw(senha.encode('utf-8'), hash_armazenado.encode('utf-8'))

    def ValidUser(self):
        login = self.Data.get('login')
        password = self.Data.get('password')
        if not login:
            return False, 'Usuário não é válido.'
        if not password:
            return False, 'Senha não é válida.'
        self.login = login
        self.password = password
        return True, ''

    def FindUser(self):
        Data = Database()
        resultado = Data.SelecionarRegistro(Usuarios, USUsername=self.login)
        if resultado and len(resultado) > 0:
            usuario = resultado[0]
            print(usuario)
            if self.verificar_senha(self.password, usuario['password']):
                return [usuario]
        return []

    def FindUsername(self, login):
        Data = Database()
        resultado = Data.SelecionarRegistro(Usuarios, USUsername=login)
        return len(resultado) > 0

    def CreateUser(self):
        response, message = self.ValidUserRegister()
        if not response:
            return 400, message

        Data = Database()
        if self.FindUsername(self.login):
            return 400, 'Já existe um usuário com este nome'

        senha_criptografada = self.hash_senha(self.password)
        response = Data.Insercao(Usuarios, USUsername=self.login, USUpassword=senha_criptografada)
        if response is None:
            return 400, 'Ocorreu um erro ao gravar registro, tente novamente.'
        else:
            return 200, 'Registro gravado com sucesso.'

    def ValidUserRegister(self):
        login = self.Data.get('login')
        password = self.Data.get('password')
        if not login:
            return False, 'Usuário não pode ser nulo.'
        if len(login) < 4:
            return False, 'Usuário não pode ter menos de 4 caracteres.'
        if self.FindUsername(login):
            return False, 'Usuário não pode ser cadastrado pois já existe outra conta com o mesmo usuário.'
        response, message = self.ValidPassword(password)
        if not response:
            return False, message
        self.login = login
        self.password = password
        return True, ''

    def ValidPassword(self, password):
        if not password:
            return False, 'Senha não é válida.'
        if len(password) < 4:
            return False, 'Senha não pode conter menos de 4 caracteres.'
        match = re.match(self.pattern, password)
        if not match:
            return False, 'Senha não contém os caracteres necessários.'
        return True, ''

    def ResetPassword(self):
        self.login = self.Data.get('login')
        self.password = self.Data.get('password')
        newPassword = self.Data.get('newPassword')

        if not self.FindUsername(self.login):
            return 400, 'Usuário não encontrado.'

        usuario = self.FindUser()
        if not usuario:
            return 400, 'Senha incorreta.'

        response, message = self.ValidPassword(newPassword)
        if not response:
            return 400, message

        senha_criptografada = self.hash_senha(newPassword)
        Data = Database()
        response = Data.DoUpdate(Usuarios, {"USUsername": self.login}, {"USUpassword": senha_criptografada})
        if response is None:
            return 400, 'Ocorreu um erro ao alterar registro. Tente novamente'
        else:
            return 200, 'Registro modificado com sucesso.'

    def FindUserById(self, idUsuario):
        Data = Database()
        response = Data.SelecionarRegistro(Usuarios, USUid=idUsuario)
        if len(response) > 0:
            return 200, response[0]
        else:
            return 400, 'Usuário não encontrado.'