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
        dataSetOriginal = pd.read_csv(rf'C:\Users\amjun\Desktop\Catolica\TCC\TCCPrivado\arquivos\datasets\DataSetOriginal.csv',sep=';',encoding='latin')
        
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
                                
                ArrayProdutosOriginal = []
                for produtoItem in produtos_recomendados:
                    codigoProduto = produtoItem[0].CodigoProduto
                    produtoOriginal = dataSetOriginal[dataSetOriginal['codprod'] == codigoProduto]
                    
                    if not produtoOriginal.empty:
                        produto_info = produtoOriginal.iloc[0].to_dict()  # Converte a Series em dicionário
                        ArrayProdutosOriginal.append(produto_info)
                    else:
                        print(f"Produto com código {codigoProduto} não encontrado.")

                recomendacoes.append({
                    'ProdutoBase': {
                        'CodigoProduto': int(item_base['CodigoProduto']),
                        'DescricaoProduto': item_base['DescricaoProduto'],
                        'Marca': item_base['Marca'],
                        'Departamento': item_base['DescricaoDepartamento'],
                        'Seção': item_base['DescricaoSecao']
                    },
                    'Recomendacoes': [
                        {
                            'CodigoProduto': produto['codprod'],
                            'DescricaoProduto': produto['descricaoproduto'],
                            'Marca': produto['marca'],
                            'Departamento': produto['deptodescricao'],
                            'Seção': produto['secdescricao']
                        } for produto in ArrayProdutosOriginal
                    ]
                })
        return recomendacoes
