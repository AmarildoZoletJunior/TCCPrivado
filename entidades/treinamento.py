
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.decomposition import PCA
from sklearn.neighbors import NearestNeighbors
import matplotlib.pyplot as plt
import seaborn as sns


from config import  configuration
import numpy as np
import joblib
import pandas as pd

class AlgoritmoKNN():
    def __init__(self, Data, NumPCA, QtdeRecomendacao):
        self.DataSet = Data
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
        
        FatorPesoVariaveis = np.array([5, 8])
        VariveisBalanceadas = EscalarVariaveisNumericas * FatorPesoVariaveis
        
        self.FeaturesCombinadas = np.hstack([TFReduzido, EncoderCategorico, VariveisBalanceadas])

        self.Modelo = NearestNeighbors(n_neighbors=self.QtdeRecomendacao + 1, metric='nan_euclidean') 
        self.Modelo.fit(self.FeaturesCombinadas)
        
        joblib.dump(VetorTF, f'{configuration.UrlPastaParametros}/vetor_tfidf.pkl')
        joblib.dump(pca, f'{configuration.UrlPastaParametros}/pca_transform.pkl')
        joblib.dump(Scaler, f'{configuration.UrlPastaParametros}/standard_scaler.pkl')
        joblib.dump(Encoder, f'{configuration.UrlPastaParametros}/onehot_encoder.pkl')
        joblib.dump(self.Modelo, f'{configuration.UrlPastaModelos}/modelo_knn.pkl')
        csv_path = f'{configuration.UrlPastaDataSet}/dataSetTreinamento.csv'
        self.DataSet.to_csv(csv_path, index=False, encoding='utf-8')
        return 200,''
        


    def RecomendarProdutosPorCodigo(self, codigo_produto):
        caminho_modelo = f'{configuration.UrlPastaModelos}/modelo_knn.pkl'
        caminho_tfidf = f'{configuration.UrlPastaParametros}/vetor_tfidf.pkl'
        caminho_pca = f'{configuration.UrlPastaParametros}/pca_transform.pkl'
        caminho_scaler = f'{configuration.UrlPastaParametros}/standard_scaler.pkl'
        caminho_encoder = f'{configuration.UrlPastaParametros}/onehot_encoder.pkl'
        caminho_dataset = f'{configuration.UrlPastaDataSet}/dataSetTreinamento.csv'
        
        arquivos_necessarios = [caminho_modelo, caminho_tfidf, caminho_pca, caminho_scaler, caminho_encoder, caminho_dataset]
        for arquivo in arquivos_necessarios:
            if not os.path.exists(arquivo):
                return 400, f"Arquivo '{arquivo}' não encontrado. Treine o algoritmo antes de recomendar produtos."
            
        self.Modelo = joblib.load(caminho_modelo)
        self.TfidfVectorizer = joblib.load(caminho_tfidf)
        self.PCA = joblib.load(caminho_pca)
        self.Scaler = joblib.load(caminho_scaler)
        self.Encoder = joblib.load(caminho_encoder)
        self.DataSet = pd.read_csv(caminho_dataset, delimiter=',')
        
        produto = self.DataSet[self.DataSet['CodigoProduto'] == codigo_produto]
        if produto.empty:
            return 400, f"Produto com código {codigo_produto} não encontrado."
        
        descricao = produto['DescricaoProduto'].values[0]
        peso_embalagem = produto['PesoEmbalagemUnitaria'].values[0]
        qtde_embalagem = produto['QtdeEmbalagem'].values[0]
        cod_departamento = produto['CodDepartamento'].values[0]
        cod_secao = produto['CodSecao'].values[0]
        
        tfidf_matrix = self.TfidfVectorizer.transform([descricao])
        tfidf_reduced = self.PCA.transform(tfidf_matrix.toarray())
        
        variaveis_numericas = pd.DataFrame([[peso_embalagem, qtde_embalagem]], columns=['PesoEmbalagemUnitaria', 'QtdeEmbalagem'])
        variaveis_numericas_escaladas = self.Scaler.transform(variaveis_numericas) * np.array([5, 8])
        
        variaveis_categoricas = pd.DataFrame([[cod_departamento, cod_secao]], columns=['CodDepartamento', 'CodSecao'])
        variaveis_categoricas_codificadas = self.Encoder.transform(variaveis_categoricas)
        
        features_produto = np.hstack([tfidf_reduced, variaveis_categoricas_codificadas, variaveis_numericas_escaladas])
        
        distancias, indices = self.Modelo.kneighbors(features_produto)
        
        informacoes_produto_base = {
            "CodigoProduto": codigo_produto,
            "Descricao": produto['DescricaoProduto'].values[0],
            "PesoUnitario": float(produto['PesoEmbalagemUnitaria'].values[0]),
            "QtdeEmbalagem": int(produto['QtdeEmbalagem'].values[0]),
            "Secao": produto['DescricaoSecao'].values[0],
            "Departamento": produto['DescricaoDepartamento'].values[0],
            "Marca": produto['Marca'].values[0]
        }
        
        produtosInformacoesLista = []
        produtos_recomendados = self.DataSet.iloc[indices[0]]['CodigoProduto'].tolist()

        iguais_departamento_secao = 0  
        iguais_qtde_embalagem = 0
        iguais_peso_unitario = 0

        margem_relativa = 0.10 * float(produto['PesoEmbalagemUnitaria'].values[0])  
        peso_unitario_minimo = float(produto['PesoEmbalagemUnitaria'].values[0]) - margem_relativa
        peso_unitario_maximo = float(produto['PesoEmbalagemUnitaria'].values[0]) + margem_relativa

        for i, CodigoProdutoRecomendado in enumerate(produtos_recomendados):
            if CodigoProdutoRecomendado != codigo_produto and distancias[0][i] < 0.92:
                produtoRecomendado = self.DataSet[self.DataSet['CodigoProduto'] == CodigoProdutoRecomendado]
                if len(produtoRecomendado) > 0:
                    informacoesProduto = {
                        "CodigoProduto": CodigoProdutoRecomendado,
                        "Descricao": produtoRecomendado['DescricaoProduto'].values[0],
                        "PesoUnitario": float(produtoRecomendado['PesoEmbalagemUnitaria'].values[0]),
                        "QtdeEmbalagem": int(produtoRecomendado['QtdeEmbalagem'].values[0]),
                        "Secao": produtoRecomendado['DescricaoSecao'].values[0],
                        "Departamento": produtoRecomendado['DescricaoDepartamento'].values[0],
                        "Marca": produtoRecomendado['Marca'].values[0]
                    }
                    produtosInformacoesLista.append(informacoesProduto)

                    if (produtoRecomendado['CodDepartamento'].values[0] == cod_departamento and 
                        produtoRecomendado['CodSecao'].values[0] == cod_secao):
                        iguais_departamento_secao += 1
                    
                    peso_unitario_recomendado = float(produtoRecomendado['PesoEmbalagemUnitaria'].values[0])
                    if peso_unitario_minimo <= peso_unitario_recomendado <= peso_unitario_maximo:
                        iguais_peso_unitario += 1
                    if produtoRecomendado['QtdeEmbalagem'].values[0] == qtde_embalagem:
                        iguais_qtde_embalagem += 1

        total_recomendados = len(produtosInformacoesLista)
        
        if total_recomendados > 0:
            porcentagem_iguais_departamento_secao = (iguais_departamento_secao / total_recomendados) * 100
            porcentagem_iguais_qtde_embalagem = (iguais_qtde_embalagem / total_recomendados) * 100
            porcentagem_iguais_peso_unitario = (iguais_peso_unitario / total_recomendados) * 100
        else:
            porcentagem_iguais_departamento_secao = 0.0
            porcentagem_iguais_qtde_embalagem = 0.0
            porcentagem_iguais_peso_unitario = 0.0

        if total_recomendados > 0:
            return 200, {
                "ProdutoBase": informacoes_produto_base,
                "Recomendacoes": produtosInformacoesLista,
                "PorcentagemAcertoDepartamentoESecao": porcentagem_iguais_departamento_secao,
                "PorcentagemAcertoQtdeEmbalagem": porcentagem_iguais_qtde_embalagem,
                "PorcentagemPesoUnitarioAproximado": porcentagem_iguais_peso_unitario
            }
        else:
            return 400, 'Não foi encontrado nenhum produto similar ao item selecionado.'
        
    def RecomendarTodosProdutos(self):
        caminho_modelo = f'{configuration.UrlPastaModelos}/modelo_knn.pkl'
        caminho_tfidf = f'{configuration.UrlPastaParametros}/vetor_tfidf.pkl'
        caminho_pca = f'{configuration.UrlPastaParametros}/pca_transform.pkl'
        caminho_scaler = f'{configuration.UrlPastaParametros}/standard_scaler.pkl'
        caminho_encoder = f'{configuration.UrlPastaParametros}/onehot_encoder.pkl'
        caminho_dataset = f'{configuration.UrlPastaDataSet}/dataSetTreinamento.csv'
        
        arquivos_necessarios = [caminho_modelo, caminho_tfidf, caminho_pca, caminho_scaler, caminho_encoder, caminho_dataset]
        for arquivo in arquivos_necessarios:
            if not os.path.exists(arquivo):
                return 400, f"Arquivo '{arquivo}' não encontrado. Treine o algoritmo antes de recomendar produtos.", ''

        # Carregar os objetos do disco
        self.Modelo = joblib.load(caminho_modelo)
        self.TfidfVectorizer = joblib.load(caminho_tfidf)
        self.PCA = joblib.load(caminho_pca)
        self.Scaler = joblib.load(caminho_scaler)
        self.Encoder = joblib.load(caminho_encoder)
        self.DataSet = pd.read_csv(caminho_dataset, delimiter=',')
        
        todas_recomendacoes = []
        iguais_departamento_secao = 0
        iguais_qtde_embalagem = 0
        iguais_peso_unitario = 0
        QtdeTotalRecomendacoes = 0
        
        for index, produto in self.DataSet.iterrows():
            codigo_produto = produto['CodigoProduto']
            descricao = produto['DescricaoProduto']
            peso_embalagem_unitaria = produto['PesoEmbalagemUnitaria']
            qtde_embalagem = produto['QtdeEmbalagem']
            cod_departamento = produto['CodDepartamento']
            cod_secao = produto['CodSecao']
            
            tfidf_matrix = self.TfidfVectorizer.transform([descricao])
            tfidf_reduced = self.PCA.transform(tfidf_matrix.toarray())
            
            variaveis_numericas = pd.DataFrame([[peso_embalagem_unitaria, qtde_embalagem]], columns=['PesoEmbalagemUnitaria', 'QtdeEmbalagem'])
            variaveis_categoricas = pd.DataFrame([[cod_departamento, cod_secao]], columns=['CodDepartamento', 'CodSecao'])
            
            variaveis_numericas_escaladas = self.Scaler.transform(variaveis_numericas) * np.array([5, 8])
            variaveis_categoricas_codificadas = self.Encoder.transform(variaveis_categoricas)
            
            features_produto = np.hstack([tfidf_reduced, variaveis_categoricas_codificadas, variaveis_numericas_escaladas])
            
            distancias, indices = self.Modelo.kneighbors(features_produto)
            
            informacoes_produto_base = {
                "CodigoProduto": codigo_produto,
                "Descricao": produto['DescricaoProduto'],
                "PesoUnitario": float(produto['PesoEmbalagemUnitaria']),
                "QtdeEmbalagem": int(produto['QtdeEmbalagem']),
                "Secao": produto['DescricaoSecao'],
                "Departamento": produto['DescricaoDepartamento'],
                "Marca": produto['Marca']
            }

            produtos_informacoes_lista = []
            for i, CodigoProdutoRecomendado in enumerate(self.DataSet.iloc[indices[0]]['CodigoProduto'].tolist()):
                if CodigoProdutoRecomendado != codigo_produto and distancias[0][i] < 0.92:  # Filtragem pela distância
                    produto_recomendado = self.DataSet[self.DataSet['CodigoProduto'] == CodigoProdutoRecomendado]
                    if len(produto_recomendado) > 0:
                        peso_recomendado = float(produto_recomendado['PesoEmbalagemUnitaria'].values[0])
                        peso_unitario_base = float(produto['PesoEmbalagemUnitaria'])
                        margem_relativa = 0.10 * peso_unitario_base

                        peso_unitario_minimo = peso_unitario_base - margem_relativa
                        peso_unitario_maximo = peso_unitario_base + margem_relativa

                        informacoes_produto = {
                            "CodigoProduto": CodigoProdutoRecomendado,
                            "Descricao": produto_recomendado['DescricaoProduto'].values[0],
                            "PesoUnitario": peso_recomendado,
                            "QtdeEmbalagem": int(produto_recomendado['QtdeEmbalagem'].values[0]),
                            "Secao": produto_recomendado['DescricaoSecao'].values[0],
                            "Departamento": produto_recomendado['DescricaoDepartamento'].values[0],
                            "Marca": produto_recomendado['Marca'].values[0]
                        }
                        produtos_informacoes_lista.append(informacoes_produto)
                        QtdeTotalRecomendacoes += 1

                        if (produto_recomendado['CodDepartamento'].values[0] == cod_departamento and 
                            produto_recomendado['CodSecao'].values[0] == cod_secao):
                            iguais_departamento_secao += 1

                        if produto_recomendado['QtdeEmbalagem'].values[0] == qtde_embalagem:
                            iguais_qtde_embalagem += 1

                        if peso_unitario_minimo <= peso_recomendado <= peso_unitario_maximo:
                            iguais_peso_unitario += 1

            if len(produtos_informacoes_lista) > 0:
                todas_recomendacoes.append({
                    "ProdutoBase": informacoes_produto_base,
                    "Recomendacoes": produtos_informacoes_lista
                })

        if QtdeTotalRecomendacoes > 0:
            porcentagem_iguais_departamento_secao = (iguais_departamento_secao / QtdeTotalRecomendacoes) * 100
            porcentagem_iguais_qtde_embalagem = (iguais_qtde_embalagem / QtdeTotalRecomendacoes) * 100
            porcentagem_iguais_peso_unitario = (iguais_peso_unitario / QtdeTotalRecomendacoes) * 100
        else:
            porcentagem_iguais_departamento_secao = 0.0
            porcentagem_iguais_qtde_embalagem = 0.0
            porcentagem_iguais_peso_unitario = 0.0
        return 200, todas_recomendacoes, {
            "PorcentagemIguaisDepartamentoESecao": porcentagem_iguais_departamento_secao,
            "PorcentagemQtdeEmbalagem": porcentagem_iguais_qtde_embalagem,
            "PorcentagemPesoUnitarioAproximados": porcentagem_iguais_peso_unitario
        }



    def PrecisaoEmK(self,Recomendado, Relevante, k):
        RecomendadoEmK = Recomendado[:k]
        Precisao = len(set(RecomendadoEmK) & set(Relevante)) / k
        return Precisao

    def RecallEmK(self,Recomendado, Relevante, k):
        RecomendadoEmK = Recomendado[:k]
        Recall = len(set(RecomendadoEmK) & set(Relevante)) / len(Relevante)
        return Recall
    
    