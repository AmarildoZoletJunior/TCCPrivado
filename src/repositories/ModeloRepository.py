


import base64
import io
import joblib
import numpy as np
import pandas as pd

from src.entidades.modelos import Modelos
from src.entidades.tratamentoDados import ManipulacaoCSV
from src.repositories.UsuarioRepository import UserRepository
from src.repositories.ArquivoRepository import ArquivoRepository
from src.data.database import Database

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.decomposition import PCA
from sklearn.neighbors import NearestNeighbors

class ModeloRepository():
    def __init__(self,request):
        self.request = request  
        
    def ValidarInformacoes(self,idArquivo,versao,idUsuario,numPca,qtdeRecomendacao):
        
        if not idArquivo:
             return False,'Parâmetro idArquivo é obrigatório.'      
              
        if not versao:
            return False,'Parâmetro versao é obrigatório.'
            
        if not idUsuario:
            return False,'Parâmetro idUsuario é obrigatório.'
        
        if not numPca:
            return False,'Parâmetro numPca é obrigatório.'

        if not qtdeRecomendacao:
            return False,'Parâmetro qtdeRecomendacao é obrigatório.'
        
        if not isinstance(qtdeRecomendacao,int):
            return False,'Parâmetro qtdeRecomendacao pode ser apenas do tipo inteiro'
        
        if not isinstance(numPca,int):
            return False,'Parâmetro numPca pode ser apenas do tipo inteiro'
        
        if not isinstance(idUsuario,int):
            return False,'Parâmetro idUsuario pode ser apenas do tipo inteiro'
        
        if not isinstance(versao,str):
            return False,'Parâmetro versao pode ser apenas texto.'
        
        if not isinstance(idArquivo,int):
            return False,'Parâmetro idArquivo pode ser apenas do tipo inteiro'
        
        return True,''
        
        
    def CriarModelo(self):
        idArquivo = self.request.get('idArquivo')
        versao = self.request.get('versao')
        idUsuario = self.request.get('idUsuario')
        numPca = self.request.get('numPca')
        qtdeRecomendacao = self.request.get('qtdeRecomendacao')
        
        
        response,message = self.ValidarInformacoes(idArquivo,versao,idUsuario,numPca,qtdeRecomendacao)
        if not response:
            return 400,message
        
        arquivoRepository = ArquivoRepository('')
        response,message,data = arquivoRepository.ListarArquivoUnico(idArquivo)
        if response == 400:
            return response,message
        
        usuarioRepository = UserRepository('')
        response,message = usuarioRepository.FindUserById(idUsuario)
        if response == 400:
            return response,message
        CsvConteudoBinario = data[0]['arquivo']
        delimiter = data[0]['delimiter']
        CsvConteudoBytes = base64.b64decode(CsvConteudoBinario)
        ConteudoCSVTexto = CsvConteudoBytes.decode('ISO-8859-1')
        DataSet = pd.read_csv(io.StringIO(ConteudoCSVTexto), delimiter=delimiter)
        
        ManipulacaoDados = ManipulacaoCSV(DataSet)
        response, message = ManipulacaoDados.validarDadosCSV()
        if not response:
            return 400, message

        response, message, dataSetTratado = ManipulacaoDados.tratamentoCSV()
        if not response:
            return 400,message
        
        
        if len(dataSetTratado) < 4:
            return 400,'Não foi possível treinar um modelo pois a quantidade de registros é menor que 4.'
        
        if len(dataSetTratado) < numPca:
            return 400,'Não foi possível treinar um modelo pois o numPca é superior a quantidade de registros.'
        
        if len(dataSetTratado) < qtdeRecomendacao:
            return 400,'Não foi possível treinar um modelo pois o qtdeRecomendacao é superior a quantidade de registros.'
        
        VetorTF = TfidfVectorizer()
        VetorTFMatrix = VetorTF.fit_transform(dataSetTratado['DescricaoProduto'])

        pca = PCA(n_components=numPca)
        TFReduzido = pca.fit_transform(VetorTFMatrix.toarray())
        
        VariaveisNumericas = dataSetTratado[['PesoEmbalagemUnitaria', 'QtdeEmbalagem']]
        Scaler = StandardScaler()
        EscalarVariaveisNumericas = Scaler.fit_transform(VariaveisNumericas)

        VariveisCategoricas = dataSetTratado[['CodDepartamento', 'CodSecao']]
        Encoder = OneHotEncoder(sparse_output=False)
        EncoderCategorico = Encoder.fit_transform(VariveisCategoricas)
        
        FatorPesoVariaveis = np.array([5, 8])
        VariveisBalanceadas = EscalarVariaveisNumericas * FatorPesoVariaveis
        
        FeaturesCombinadas = np.hstack([TFReduzido, EncoderCategorico, VariveisBalanceadas])

        Modelo = NearestNeighbors(n_neighbors=qtdeRecomendacao + 1, metric='nan_euclidean') 
        Modelo.fit(FeaturesCombinadas)
        
        CSVConteudoString = dataSetTratado.to_csv(index=False, sep=';')
        CSVConteudoBinario = CSVConteudoString.encode('ISO-8859-1')
        
        EncoderByte = self.SerializarObjeto(Encoder)
        ScalerByte = self.SerializarObjeto(Scaler)
        VetorTFByte = self.SerializarObjeto(VetorTF)
        PcaByte = self.SerializarObjeto(pca)
        ModeloByte = self.SerializarObjeto(Modelo)
        
        data = Database()
        data = data.DoInsert(Modelos,
                             MDVersao=versao,MDArquivo=ModeloByte,MDIdArquivoProd=idArquivo,MDArquivoScaler=ScalerByte,MDArquivoEncoder=EncoderByte,
                             MDArquivoPca=PcaByte,MDVetorTF=VetorTFByte,MDNumeroPCA=numPca,MDQtdeRecomendacao=qtdeRecomendacao,MDIdUsuario=idUsuario,MDArquivoProdAlterado = CSVConteudoBinario
                             )
        return 200,''
    
    def SerializarObjeto(self,obj):
        buffer = io.BytesIO()
        joblib.dump(obj, buffer)
        buffer.seek(0)
        return buffer.read()
    
    def RemoverModelo(self,idModelo):
        if not idModelo:
            return 400,'Parâmetro idModelo é obrigatório.'
        
        if not isinstance(idModelo,int):
            return 400,'Parâmetro idModelo pode ser apenas do tipo inteiro'
        data = Database()
        dataModelos = data.DoSelect(Modelos,MDId = idModelo)
        if len(dataModelos) == 0:
            return 400,f'Não foi encontrado o registro do modelo, Id: {idModelo}'
        response = data.DoDelete(Modelos,MDId = idModelo)
        if response is None:
            return 400,f'Não foi possível remover o registro, tente novamente.'
        return 200,''
        
    def RecomendacaoProdutoUnico(self):       
        idModelo = self.request.get('idModelo')
        CodigoProdutoBase = self.request.get('codigoProduto')
        if not CodigoProdutoBase:
            return 400,'Parâmetro codigoProduto é obrigatório.'
        
        if not isinstance(CodigoProdutoBase,int):
            return 400,'Parâmetro codigoProduto deve ser do tipo inteiro.'
        
                
        if not idModelo:
            return 400,'Parâmetro idModelo é obrigatório.'
        
        if not isinstance(idModelo,int):
            return 400,'Parâmetro idModelo deve ser do tipo inteiro.' 
        
        response,message,dataModelo = self.BuscarModeloPorId(idModelo)
        if response == 400:
            return response,message
    
        
        self.Modelo = joblib.load(io.BytesIO(dataModelo[0]['arquivo']))

        self.TfidfVectorizer = joblib.load(io.BytesIO(dataModelo[0]['vetor_tf']))

        self.pca = joblib.load(io.BytesIO(dataModelo[0]['pca']))

        self.Scaler = joblib.load(io.BytesIO(dataModelo[0]['scaler']))

        self.Encoder = joblib.load(io.BytesIO(dataModelo[0]['encoder']))
        
        CSVString = io.BytesIO(dataModelo[0]['arquivo_produtos_alterados'])
        
        self.DataSet = pd.read_csv(CSVString, delimiter=';', encoding='ISO-8859-1')

        
        produto = self.DataSet[self.DataSet['CodigoProduto'] == CodigoProdutoBase]
        if produto.empty:
            return 400, f"Produto com código {CodigoProdutoBase} não encontrado."
        
        descricao = produto['DescricaoProduto'].values[0]
        peso_embalagem = produto['PesoEmbalagemUnitaria'].values[0]
        qtde_embalagem = produto['QtdeEmbalagem'].values[0]
        cod_departamento = produto['CodDepartamento'].values[0]
        cod_secao = produto['CodSecao'].values[0]
        
        tfidf_matrix = self.TfidfVectorizer.transform([descricao])
        tfidf_reduced = self.pca.transform(tfidf_matrix.toarray())
        
        variaveis_numericas = pd.DataFrame([[peso_embalagem, qtde_embalagem]], columns=['PesoEmbalagemUnitaria', 'QtdeEmbalagem'])
        variaveis_numericas_escaladas = self.Scaler.transform(variaveis_numericas) * np.array([5, 8])
        
        variaveis_categoricas = pd.DataFrame([[cod_departamento, cod_secao]], columns=['CodDepartamento', 'CodSecao'])
        variaveis_categoricas_codificadas = self.Encoder.transform(variaveis_categoricas)
        
        features_produto = np.hstack([tfidf_reduced, variaveis_categoricas_codificadas, variaveis_numericas_escaladas])
        
        distancias, indices = self.Modelo.kneighbors(features_produto)
        
        informacoes_produto_base = {
            "CodigoProduto": CodigoProdutoBase,
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
            if CodigoProdutoRecomendado != CodigoProdutoBase and distancias[0][i] < 0.92:
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
        
        
        
    def BuscarModeloPorId(self,idModelo):
        if not isinstance(idModelo,int):
            return 400,'Parâmetro idModelo deve ser do tipo inteiro.',''
        
        if not idModelo:
            return 400,'Parâmetro idModelo é obrigatório.',''
        data = Database()
        dataModelos = data.DoSelect(Modelos,MDId = idModelo)
        if len(dataModelos) == 0:
            return 400,f'Não foi encontrado o registro do modelo, Id: {idModelo}',''
        return 200,'',dataModelos
    
    
    def RecomendacaoProdutosTotal(self):
        idModelo = self.request.get('idModelo')
        if not idModelo:
            return 400,'Parâmetro idModelo é obrigatório.'
        
        if not isinstance(idModelo,int):
            return 400,'Parâmetro idModelo deve ser do tipo inteiro.'
        
        
        response,message,dataModelo = self.BuscarModeloPorId(idModelo)
        if response == 400:
            return response,message
    
        
        self.Modelo = joblib.load(io.BytesIO(dataModelo[0]['arquivo']))

        self.TfidfVectorizer = joblib.load(io.BytesIO(dataModelo[0]['vetor_tf']))

        self.pca = joblib.load(io.BytesIO(dataModelo[0]['pca']))

        self.Scaler = joblib.load(io.BytesIO(dataModelo[0]['scaler']))

        self.Encoder = joblib.load(io.BytesIO(dataModelo[0]['encoder']))
        
        stringTeste = io.BytesIO(dataModelo[0]['arquivo_produtos_alterados'])
        
        self.DataSet = pd.read_csv(stringTeste, delimiter=';', encoding='ISO-8859-1')

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
            tfidf_reduced = self.pca.transform(tfidf_matrix.toarray())
            
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
            
        json = {"RecomendacaoProdutos":todas_recomendacoes,"Testes":{
            "PorcentagemIguaisDepartamentoESecao": porcentagem_iguais_departamento_secao,
            "PorcentagemQtdeEmbalagem": porcentagem_iguais_qtde_embalagem,
            "PorcentagemPesoUnitarioAproximados": porcentagem_iguais_peso_unitario
        }}
        return 200, json