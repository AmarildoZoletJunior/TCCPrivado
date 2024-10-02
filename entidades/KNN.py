import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.decomposition import PCA
from sklearn.neighbors import NearestNeighbors
from entidades.dados import DadosCSV
import numpy as np




class AlgoritmoKNN():
    def __init__(self,Data):
        self.Data = Data

    def tratamentoCSV(self):
        dadosClasse = DadosCSV()
        dadosClasse.tratamentoCSV()

    def treinamentoKNN(self):
        # Preparando a matriz TF-IDF a partir da descrição do produto
        # tfidf = TfidfVectorizer()
        # tfidf_matrix = tfidf.fit_transform(DataSet['DescricaoProduto'])

        # # Reduzindo a dimensionalidade da matriz TF-IDF
        # pca = PCA(n_components=900) 

        # tfidf_reduced = pca.fit_transform(tfidf_matrix.toarray())

        # # Codificando as variáveis categóricas
        # categorical_features = DataSet[['CodDepartamento', 'CodSecao']]
        # encoder = OneHotEncoder(sparse_output=False)
        # encoded_categorical = encoder.fit_transform(categorical_features)

        # # Combinando as características TF-IDF reduzidas e as codificadas
        # combined_features = np.hstack([tfidf_reduced, encoded_categorical])

        # # {'l2', 'cityblock', 'cosine', 'yule', 'nan_euclidean', 'pyfunc', 'canberra', 'sokalsneath', 'p', 'mahalanobis', 'braycurtis', 'l1', 'minkowski', 'dice', 'euclidean', 'seuclidean', 'russellrao', 'rogerstanimoto', 'infinity', 'jaccard', 'hamming', 'chebyshev', 'correlation', 'sokalmichener', 'precomputed', 'haversine', 'sqeuclidean', 'manhattan'}

        # # Treinando o modelo Nearest Neighbors com uma métrica de distância diferente
        # model = NearestNeighbors(n_neighbors=5, metric='nan_euclidean')
        # model.fit(combined_features)

        # TesteCodigo = 5388

        # # Encontrar o índice do produto base
        # item_base_index = DataSet[DataSet['CodigoProduto'] == TesteCodigo].index

        # # Converter o índice para posição inteira
        # position = DataSet.index.get_loc(item_base_index[0])


        # if not item_base_index.empty:
        #     item_base_index = position

        #     distances, indices = model.kneighbors([combined_features[position]])


        #     item_base = DataSet.iloc[item_base_index]

        #     print("Descrição do item base para recomendação:")
        #     print(item_base[['CodigoProduto','DescricaoProduto','Marca']])

        #     print("Descrições dos itens recomendados:")
        #     print("-----------------------------------")
        #     for idx in indices[0][1:]:
        #         print(DataSet.iloc[idx])
        #         print("-----------------------------------")
        # else:
        #     print(f"Produto com código {TesteCodigo} não encontrado no DataSet.")
        print()