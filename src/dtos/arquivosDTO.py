


import base64


class ArquivoProdutosDTO:
    def __init__(self, id, data_postagem, arquivo, delimiter, qtde_produtos, id_usuario, versao):
        self.id = id
        self.data_postagem = data_postagem
        self.arquivo = arquivo
        self.delimiter = delimiter
        self.qtde_produtos = qtde_produtos
        self.id_usuario = id_usuario
        self.versao = versao

    def to_dict(self):
        return {
            "id": self.id,
            "data_postagem": self.data_postagem,
            "arquivo": base64.b64encode(self.arquivo).decode('utf-8') ,
            "delimiter": self.delimiter,
            "qtde_produtos": self.qtde_produtos,
            "id_usuario": self.id_usuario,
            "versao": self.versao
        }