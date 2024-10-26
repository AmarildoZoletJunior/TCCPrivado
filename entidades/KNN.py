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
        VetorTF = TfidfVectorizer()
        VetorTFMatrix = VetorTF.fit_transform(self.DataSet['DescricaoProduto'])

        pca = PCA(n_components=self.NumPCA)
        TFReduzido = pca.fit_transform(VetorTFMatrix.toarray())
        
        VariaveisNumericas = self.DataSet[['PesoEmbalagemUnitaria', 'QtdeEmbalagem']]
        Scaler = StandardScaler()
        EscalarVariaveisNumericas = Scaler.fit_transform(VariaveisNumericas)

        VariveisCategoricas = self.DataSet[['CodDepartamento', 'CodSecao']]
        Encoder = OneHotEncoder(sparse_output=False)
        EncoderCategorico = Encoder.fit_transform(VariveisCategoricas)
        
        FatorPesoVariaveis = np.array([5,5])
        VariveisBalanceadas = EscalarVariaveisNumericas * FatorPesoVariaveis
        
        self.FeaturesCombinadas = np.hstack([TFReduzido, EncoderCategorico, VariveisBalanceadas])

        self.Modelo = NearestNeighbors(n_neighbors=self.QtdeRecomendacao + 1, metric='nan_euclidean') 

        self.Modelo.fit(self.FeaturesCombinadas)

    def recomendarTodosProdutos(self):
        Recomendacoes = []
        DataSetOriginal = pd.read_csv(rf'C:\Users\amjun\Desktop\Catolica\TCC\TCCPrivado\arquivos\DataSet\DataSetOriginal.csv',sep=';',encoding='latin')
        for Index, Produto in self.DataSet.iterrows():
            CodigoProduto = Produto['CodigoProduto']
            IndexProduto = self.DataSet[self.DataSet['CodigoProduto'] == CodigoProduto].index
            if not IndexProduto.empty:
                Posicao = IndexProduto[0]
                Distancia, Indice = self.Modelo.kneighbors([self.FeaturesCombinadas[Posicao]])
                RegistroItemBase = self.DataSet.loc[Posicao]
                
                
                if len(Indice[0]) > 1:
                    IndiceSimilares = [i for i in Indice[0] if i != Posicao]
                    DistanciasSimilares = [d for i, d in zip(Indice[0], Distancia[0]) if i != Posicao]
                else:
                    IndiceSimilares = []
                    DistanciasSimilares = []


                ProdutosRecomendados = [
                    (produto, distancia) for produto, distancia in zip(self.DataSet.loc[IndiceSimilares].itertuples(index=False), DistanciasSimilares) 
                    if distancia <= 0.88
                ]
                                
                ArrayProdutosOriginal = []
                for produtoItem in ProdutosRecomendados:
                    codigoProduto = produtoItem[0].CodigoProduto
                    produtoOriginal = DataSetOriginal[DataSetOriginal['codprod'] == codigoProduto]
                    
                    if not produtoOriginal.empty:
                        produto_info = produtoOriginal.iloc[0].to_dict()
                        ArrayProdutosOriginal.append(produto_info)
                    else:
                        print(f"Produto com código {codigoProduto} não encontrado.")

                Recomendacoes.append({
                    'ProdutoBase': {
                        'CodigoProduto': int(RegistroItemBase['CodigoProduto']),
                        'DescricaoProduto': RegistroItemBase['DescricaoProduto'],
                        'Marca': RegistroItemBase['Marca'],
                        'Departamento': RegistroItemBase['DescricaoDepartamento'],
                        'Seção': RegistroItemBase['DescricaoSecao'],
                        'PesoProdutoUnitario':  f"{float(RegistroItemBase['PesoEmbalagemUnitaria'])} KG" if  float(RegistroItemBase['PesoEmbalagemUnitaria']) >= 1 else f"{float(RegistroItemBase['PesoEmbalagemUnitaria'])} G",
                        'QtdeEmbalagem':int(RegistroItemBase['QtdeEmbalagem']),
                    },
                    'Recomendacoes': [
                        {
                            'CodigoProduto': produto['codprod'],
                            'DescricaoProduto': produto['descricaoproduto'],
                            'Marca': produto['marca'],
                            'Departamento': produto['deptodescricao'],
                            'Seção': produto['secdescricao'],
                            'TipoEmbalagem':produto['embalagem']
                        } for produto in ArrayProdutosOriginal
                    ]
                })
        return Recomendacoes
