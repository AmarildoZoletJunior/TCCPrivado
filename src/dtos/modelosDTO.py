class ModelosDTO:
    def __init__(self, id, versao, arquivo, id_arquivo_prod,arquivo_produto_alterado, scaler, encoder, pca, vetor_tf, num_pca, qtde_recomendacao, id_usuario, data_postagem):
        self.id = id
        self.versao = versao
        self.arquivo = arquivo
        self.id_arquivo_prod = id_arquivo_prod
        self.scaler = scaler
        self.encoder = encoder
        self.pca = pca
        self.vetor_tf = vetor_tf
        self.num_pca = num_pca
        self.qtde_recomendacao = qtde_recomendacao
        self.id_usuario = id_usuario
        self.data_postagem = data_postagem
        self.arquivo_produto_alterado = arquivo_produto_alterado

    def to_dict(self):
        return {
            "id": self.id,
            "versao": self.versao,
            "arquivo": self.arquivo,
            "id_arquivo_prod": self.id_arquivo_prod,
            "scaler": self.scaler,
            "encoder": self.encoder,
            "pca": self.pca,
            "vetor_tf": self.vetor_tf,
            "num_pca": self.num_pca,
            "qtde_recomendacao": self.qtde_recomendacao,
            "id_usuario": self.id_usuario,
            "data_postagem": self.data_postagem,
            "arquivo_produtos_alterados":self.arquivo_produto_alterado
        }
