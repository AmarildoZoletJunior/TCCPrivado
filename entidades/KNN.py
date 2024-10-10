import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.decomposition import PCA
from sklearn.neighbors import NearestNeighbors
import numpy as np


class AlgoritmoKNN():
    def __init__(self, Data, NumPCA, QtdeRecomendacao):
        self.DataSet = Data.reset_index(drop=True)
        self.NumPCA = NumPCA
        self.QtdeRecomendacao = QtdeRecomendacao

    def treinamentoKNN(self):
        tfidf = TfidfVectorizer()
        tfidf_matrix = tfidf.fit_transform(self.DataSet['DescricaoProduto'])

        pca = PCA(n_components=self.NumPCA)
        tfidf_reduced = pca.fit_transform(tfidf_matrix.toarray())

        categorical_features = self.DataSet[['CodDepartamento', 'CodSecao']]
        encoder = OneHotEncoder(sparse_output=False)
        encoded_categorical = encoder.fit_transform(categorical_features)

        self.combined_features = np.hstack([tfidf_reduced, encoded_categorical])

        self.model = NearestNeighbors(n_neighbors=self.QtdeRecomendacao + 1, metric='nan_euclidean') 

        self.model.fit(self.combined_features)

    def recomendarTodosProdutos(self):
        recomendacoes = []
        
        for idx, produto in self.DataSet.iterrows():
            codigo_produto = produto['CodigoProduto']
            
            
            item_base_index = self.DataSet[self.DataSet['CodigoProduto'] == codigo_produto].index
            if not item_base_index.empty:
                position = item_base_index[0]
                distances, indices = self.model.kneighbors([self.combined_features[position]])

                item_base = self.DataSet.loc[position]
                
                if len(indices[0]) > 1:
                    similar_indices = [i for i in indices[0] if i != position]
                    similar_distances = [d for i, d in zip(indices[0], distances[0]) if i != position]
                else:
                    similar_indices = []
                    similar_distances = []


                produtos_recomendados = [
                    (produto, distancia) for produto, distancia in zip(self.DataSet.loc[similar_indices].itertuples(index=False), similar_distances) 
                    if distancia <= 0.88
                ]

                recomendacoes.append({
                    'ProdutoBase': {
                        'CodigoProduto': int(item_base['CodigoProduto']),
                        'DescricaoProduto': item_base['DescricaoProduto'],
                        'Marca': item_base['Marca'],
                    },
                    'Recomendacoes': [
                        {
                            'CodigoProduto': int(produto.CodigoProduto),
                            'DescricaoProduto': produto.DescricaoProduto,
                            'Marca': produto.Marca,
                            'Distancia': float(distancia)
                        } for produto, distancia in produtos_recomendados
                    ]
                })

            else:
                print(f"Produto com código {codigo_produto} não encontrado no DataSet.")
        
        return recomendacoes



    # def recomendarTodosProdutos(self):
    #     recomendacoes = []
        
    #     # Iterar sobre cada registro no DataSet
    #     for idx, produto in self.DataSet.iterrows():
    #         codigo_produto = produto['CodigoProduto']
            
    #         # Encontrar o índice do produto base
    #         item_base_index = self.DataSet[self.DataSet['CodigoProduto'] == codigo_produto].index
    #         if not item_base_index.empty:
    #             position = item_base_index[0]  # Pega o primeiro índice encontrado (agora deve estar sincronizado)
    #             distances, indices = self.model.kneighbors([self.combined_features[position]])

    #             item_base = self.DataSet.loc[position]  # Acessa diretamente pela posição no DataFrame (sincronizada)
    #             print(distances)
    #             # Verifica se há vizinhos suficientes
    #             if len(indices[0]) > 1:
    #                 # Ignora o próprio produto base (índice 0), e pega os próximos vizinhos
    #                 similar_indices = [i for i in indices[0] if i != position]
    #             else:
    #                 similar_indices = []

    #             # Produtos recomendados
    #             produtos_recomendados = self.DataSet.loc[similar_indices][['CodigoProduto']]
    #             recomendacoes.append({
    #                 'ProdutoBase': {
    #                     'CodigoProduto': int(item_base['CodigoProduto'])
    #                 },
    #                 'Recomendacoes': produtos_recomendados.to_dict(orient='records'),
    #             })

    #         else:
    #             print(f"Produto com código {codigo_produto} não encontrado no DataSet.")
    #     return recomendacoes  # Retorna o JSON com todas as recomendações