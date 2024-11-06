
import base64
import io

import joblib
import numpy as np
import pandas as pd

from sklearn.decomposition import PCA
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.data.database import Database
from src.entidades.modelos import Modelos
from src.entidades.tratamentoDados import ManipulacaoCSV
from src.repositories.ArquivoRepository import ArquivoRepository
from src.repositories.UsuarioRepository import UserRepository


class ModeloRepository():
    def __init__(self,request):
        self.Requisicao = request  
        
    def ValidarInformacoes(self,IdArquivo,Versao,IdUsuario,NumPca,QtdeRecomendacao):
        
        if not IdArquivo:
             return False,'Parâmetro idArquivo é obrigatório.'      
            
        if not IdUsuario:
              return False,'Parâmetro IdUsuario é obrigatório.'      
          
        if not Versao:
            return False,'Parâmetro versao é obrigatório.'
        
        if not NumPca:
            return False,'Parâmetro numPca é obrigatório.'

        if not QtdeRecomendacao:
            return False,'Parâmetro qtdeRecomendacao é obrigatório.'
        
        if not isinstance(QtdeRecomendacao,int):
            return False,'Parâmetro qtdeRecomendacao pode ser apenas do tipo inteiro'
        
        if not isinstance(NumPca,int):
            return False,'Parâmetro numPca pode ser apenas do tipo inteiro'
        
        if not isinstance(IdUsuario,int):
            return False,'Parâmetro idUsuario pode ser apenas do tipo inteiro'
        
        if not isinstance(Versao,str):
            return False,'Parâmetro versao pode ser apenas texto.'
        
        if not isinstance(IdArquivo,int):
            return False,'Parâmetro idArquivo pode ser apenas do tipo inteiro'
        
        return True,''
        
        
    def CriarModelo(self):
        IdArquivo = self.Requisicao.get('idArquivo')
        Versao = self.Requisicao.get('versao')
        IdUsuario = self.Requisicao.get('idUsuario')
        NumPca = self.Requisicao.get('numPca')
        QtdeRecomendacao = self.Requisicao.get('qtdeRecomendacao')
        
        
        Resposta,Mensagem = self.ValidarInformacoes(IdArquivo,Versao,IdUsuario,NumPca,QtdeRecomendacao)
        if not Resposta:
            return 400,Mensagem
        
        ArquivoRep = ArquivoRepository('')
        Resposta,Mensagem,data = ArquivoRep.ListarArquivoUnico(IdArquivo)
        if Resposta == 400:
            return Resposta,Mensagem
        
        UsuarioRep = UserRepository('')
        Resposta,Mensagem = UsuarioRep.FindUserById(IdUsuario)
        if Resposta == 400:
            return Resposta,Mensagem
        CsvConteudoBinario = data[0]['arquivo']
        Delimitador = data[0]['delimiter']
        CsvConteudoBytes = base64.b64decode(CsvConteudoBinario)
        ConteudoCSVTexto = CsvConteudoBytes.decode('ISO-8859-1')
        DataSet = pd.read_csv(io.StringIO(ConteudoCSVTexto), delimiter=Delimitador)
        
        ManipulacaoDados = ManipulacaoCSV(DataSet)
        Resposta, Mensagem = ManipulacaoDados.validarDadosCSV()
        if not Resposta:
            return 400, Mensagem

        Resposta, Mensagem, dataSetTratado = ManipulacaoDados.tratamentoCSV()
        if not Resposta:
            return 400,Mensagem
        
        
        if len(dataSetTratado) < 4:
            return 400,'Não foi possível treinar um modelo pois a quantidade de registros é menor que 4.'
        
        if len(dataSetTratado) < NumPca:
            return 400,'Não foi possível treinar um modelo pois o numPca é superior a quantidade de registros.'
        
        if len(dataSetTratado) < QtdeRecomendacao:
            return 400,'Não foi possível treinar um modelo pois o qtdeRecomendacao é superior a quantidade de registros.'
        
        VetorTF = TfidfVectorizer()
        VetorTFMatrix = VetorTF.fit_transform(dataSetTratado['DescricaoProduto'])

        pca = PCA(n_components=NumPca)
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

        Modelo = NearestNeighbors(n_neighbors=QtdeRecomendacao + 1, metric='nan_euclidean') 
        Modelo.fit(FeaturesCombinadas)
        
        CSVConteudoString = dataSetTratado.to_csv(index=False, sep=';')
        CSVConteudoBinario = CSVConteudoString.encode('ISO-8859-1')
        
        EncoderByte = self.SerializarObjeto(Encoder)
        ScalerByte = self.SerializarObjeto(Scaler)
        VetorTFByte = self.SerializarObjeto(VetorTF)
        PcaByte = self.SerializarObjeto(pca)
        ModeloByte = self.SerializarObjeto(Modelo)
        
        data = Database()
        data = data.Insercao(Modelos,
                             MDVersao=Versao,MDArquivo=ModeloByte,MDIdArquivoProd=IdArquivo,MDArquivoScaler=ScalerByte,MDArquivoEncoder=EncoderByte,
                             MDArquivoPca=PcaByte,MDVetorTF=VetorTFByte,MDNumeroPCA=NumPca,MDQtdeRecomendacao=QtdeRecomendacao,MDIdUsuario=IdUsuario,MDArquivoProdAlterado = CSVConteudoBinario
                             )
        return 200,''
    
    def SerializarObjeto(self,Objeto):
        Buffer = io.BytesIO()
        joblib.dump(Objeto, Buffer)
        Buffer.seek(0)
        return Buffer.read()
    
    def RemoverModelo(self,IdModelo):
        if not IdModelo:
            return 400,'Parâmetro idModelo é obrigatório.'
        
        if not isinstance(IdModelo,int):
            return 400,'Parâmetro idModelo pode ser apenas do tipo inteiro'
        BaseDados = Database()
        RegistrosModelos = BaseDados.SelecionarRegistro(Modelos,MDId = IdModelo)
        if len(RegistrosModelos) == 0:
            return 400,f'Não foi encontrado o registro do modelo, Id: {IdModelo}'
        Resposta = BaseDados.DeletarRegistro(Modelos,MDId = IdModelo)
        if Resposta is None:
            return 400,f'Não foi possível remover o registro, tente novamente.'
        return 200,''
        
    def RecomendacaoProdutoUnico(self):       
        IdModelo = self.Requisicao.get('idModelo')
        CodigoProdutoBase = self.Requisicao.get('codigoProduto')
        if not CodigoProdutoBase:
            return 400,'Parâmetro codigoProduto é obrigatório.'
        
        if not isinstance(CodigoProdutoBase,int):
            return 400,'Parâmetro codigoProduto deve ser do tipo inteiro.'
        
                
        if not IdModelo:
            return 400,'Parâmetro idModelo é obrigatório.'
        
        if not isinstance(IdModelo,int):
            return 400,'Parâmetro idModelo deve ser do tipo inteiro.' 
        
        Resposta,Mensagem,ResultadoModelos = self.BuscarModeloPorId(IdModelo)
        if Resposta == 400:
            return Resposta,Mensagem
    
        
        self.Modelo = joblib.load(io.BytesIO(ResultadoModelos[0]['arquivo']))

        self.TfidfVectorizer = joblib.load(io.BytesIO(ResultadoModelos[0]['vetor_tf']))

        self.Pca = joblib.load(io.BytesIO(ResultadoModelos[0]['pca']))

        self.Scaler = joblib.load(io.BytesIO(ResultadoModelos[0]['scaler']))

        self.Encoder = joblib.load(io.BytesIO(ResultadoModelos[0]['encoder']))
        
        CSVTexto = io.BytesIO(ResultadoModelos[0]['arquivo_produtos_alterados'])
        
        self.DataSet = pd.read_csv(CSVTexto, delimiter=';', encoding='ISO-8859-1')

        
        ConteudoProduto = self.DataSet[self.DataSet['CodigoProduto'] == CodigoProdutoBase]
        if ConteudoProduto.empty:
            return 400, f"Produto com código {CodigoProdutoBase} não encontrado."
        
        DescricaoProdutoBase = ConteudoProduto['DescricaoProduto'].values[0]
        PesoEmbalagemProdutoBase = ConteudoProduto['PesoEmbalagemUnitaria'].values[0]
        QtdeEmbalagemProdutoBase = ConteudoProduto['QtdeEmbalagem'].values[0]
        CodDepartamentoProdutoBase = ConteudoProduto['CodDepartamento'].values[0]
        CodSecaoProdutoBase = ConteudoProduto['CodSecao'].values[0]
        
        MatrizTfID = self.TfidfVectorizer.transform([DescricaoProdutoBase])
        TfIDReduzida = self.Pca.transform(MatrizTfID.toarray())
        
        VariaveisNumericas = pd.DataFrame([[PesoEmbalagemProdutoBase, QtdeEmbalagemProdutoBase]], columns=['PesoEmbalagemUnitaria', 'QtdeEmbalagem'])
        VariaveisNumericasEscaladas = self.Scaler.transform(VariaveisNumericas) * np.array([5, 8])
        
        VariaveisCategoricas = pd.DataFrame([[CodDepartamentoProdutoBase, CodSecaoProdutoBase]], columns=['CodDepartamento', 'CodSecao'])
        VariaveisCategoricasCodificadas = self.Encoder.transform(VariaveisCategoricas)
        
        VariaveisProdutosArray = np.hstack([TfIDReduzida, VariaveisCategoricasCodificadas, VariaveisNumericasEscaladas])
        
        Distancias, Indicas = self.Modelo.kneighbors(VariaveisProdutosArray)
        
        InformacoesProdutoBaseJson = {
            "CodigoProduto": CodigoProdutoBase,
            "Descricao": ConteudoProduto['DescricaoProduto'].values[0],
            "PesoUnitario": float(ConteudoProduto['PesoEmbalagemUnitaria'].values[0]),
            "QtdeEmbalagem": int(ConteudoProduto['QtdeEmbalagem'].values[0]),
            "Secao": ConteudoProduto['DescricaoSecao'].values[0],
            "Departamento": ConteudoProduto['DescricaoDepartamento'].values[0],
            "Marca": ConteudoProduto['Marca'].values[0]
        }
        
        ListaInformacoesProduto = []
        ProdutosRecomendados = self.DataSet.iloc[Indicas[0]]['CodigoProduto'].tolist()

        ContagemDepartamentoESecao = 0  
        ContagemQtdeEmbalagem = 0
        QtdePesoUnitario = 0

        MargemRelativa = 0.10 * float(ConteudoProduto['PesoEmbalagemUnitaria'].values[0])  
        PesoUnitarioMinimo = float(ConteudoProduto['PesoEmbalagemUnitaria'].values[0]) - MargemRelativa
        PesoUnitarioMaximo = float(ConteudoProduto['PesoEmbalagemUnitaria'].values[0]) + MargemRelativa

        for Index, CodigoProdutoRecomendado in enumerate(ProdutosRecomendados):
            if CodigoProdutoRecomendado != CodigoProdutoBase and Distancias[0][Index] < 0.92:
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
                    ListaInformacoesProduto.append(informacoesProduto)

                    if (produtoRecomendado['CodDepartamento'].values[0] == CodDepartamentoProdutoBase and 
                        produtoRecomendado['CodSecao'].values[0] == CodSecaoProdutoBase):
                        ContagemDepartamentoESecao += 1
                    
                    peso_unitario_recomendado = float(produtoRecomendado['PesoEmbalagemUnitaria'].values[0])
                    if PesoUnitarioMinimo <= peso_unitario_recomendado <= PesoUnitarioMaximo:
                        QtdePesoUnitario += 1
                    if produtoRecomendado['QtdeEmbalagem'].values[0] == QtdeEmbalagemProdutoBase:
                        ContagemQtdeEmbalagem += 1

        TotalRecomendados = len(ListaInformacoesProduto)
        
        if TotalRecomendados > 0:
            PorcentagemDepartamentoSecaoIguais = (ContagemDepartamentoESecao / TotalRecomendados) * 100
            PorcentagemQtdeEmbalagemIguais = (ContagemQtdeEmbalagem / TotalRecomendados) * 100
            ProcentagemPesoUnitarioSemelhantes = (QtdePesoUnitario / TotalRecomendados) * 100
        else:
            PorcentagemDepartamentoSecaoIguais = 0.0
            PorcentagemQtdeEmbalagemIguais = 0.0
            ProcentagemPesoUnitarioSemelhantes = 0.0

        if TotalRecomendados > 0:
            return 200, {
                "ProdutoBase": InformacoesProdutoBaseJson,
                "Recomendacoes": ListaInformacoesProduto,
                "PorcentagemAcertoDepartamentoESecao": PorcentagemDepartamentoSecaoIguais,
                "PorcentagemAcertoQtdeEmbalagem": PorcentagemQtdeEmbalagemIguais,
                "PorcentagemPesoUnitarioAproximado": ProcentagemPesoUnitarioSemelhantes
            }
        else:
            return 400, 'Não foi encontrado nenhum produto similar ao item selecionado.'
        
        
        
    def BuscarModeloPorId(self,idModelo):
        if not isinstance(idModelo,int):
            return 400,'Parâmetro idModelo deve ser do tipo inteiro.',''
        
        if not idModelo:
            return 400,'Parâmetro idModelo é obrigatório.',''
        BaseDados = Database()
        RegistroModelos = BaseDados.SelecionarRegistro(Modelos,MDId = idModelo)
        if len(RegistroModelos) == 0:
            return 400,f'Não foi encontrado o registro do modelo, Id: {idModelo}',''
        return 200,'',RegistroModelos
    
    
    def RecomendacaoProdutosTotal(self):
        IdModelo = self.Requisicao.get('idModelo')
        if not IdModelo:
            return 400,'Parâmetro idModelo é obrigatório.'
        
        if not isinstance(IdModelo,int):
            return 400,'Parâmetro idModelo deve ser do tipo inteiro.'
        
        
        Resposta,Mensagem,RegistroModelos = self.BuscarModeloPorId(IdModelo)
        if Resposta == 400:
            return Resposta,Mensagem
    
        
        self.Modelo = joblib.load(io.BytesIO(RegistroModelos[0]['arquivo']))

        self.TfidfVectorizer = joblib.load(io.BytesIO(RegistroModelos[0]['vetor_tf']))

        self.Pca = joblib.load(io.BytesIO(RegistroModelos[0]['pca']))

        self.Scaler = joblib.load(io.BytesIO(RegistroModelos[0]['scaler']))

        self.Encoder = joblib.load(io.BytesIO(RegistroModelos[0]['encoder']))
        
        CSVTexto = io.BytesIO(RegistroModelos[0]['arquivo_produtos_alterados'])
        
        self.DataSet = pd.read_csv(CSVTexto, delimiter=';', encoding='ISO-8859-1')

        TotalRecomendacoes = []
        QtdeDepartamentoESecao = 0
        QtdeEmbalagem = 0
        QtdePesoUnitario = 0
        QtdeTotalRecomendacoes = 0
        
        for Index, Produto in self.DataSet.iterrows():
            CodigoProdutoBase = Produto['CodigoProduto']
            DescricaoProdutoBase = Produto['DescricaoProduto']
            PesoEmbalagemUnitarioProdutoBase = Produto['PesoEmbalagemUnitaria']
            QtdeEmbalagemProdutoBase = Produto['QtdeEmbalagem']
            CodDepartamentoProdutoBase = Produto['CodDepartamento']
            CodSecaoProdutoBase = Produto['CodSecao']
            
            tfidf_matrix = self.TfidfVectorizer.transform([DescricaoProdutoBase])
            tfidf_reduced = self.Pca.transform(tfidf_matrix.toarray())
            
            VariaveisNumericas = pd.DataFrame([[PesoEmbalagemUnitarioProdutoBase, QtdeEmbalagemProdutoBase]], columns=['PesoEmbalagemUnitaria', 'QtdeEmbalagem'])
            VariaveisCategoricas = pd.DataFrame([[CodDepartamentoProdutoBase, CodSecaoProdutoBase]], columns=['CodDepartamento', 'CodSecao'])
            
            VariaveisNumericasEscaladas = self.Scaler.transform(VariaveisNumericas) * np.array([5, 8])
            VariveisCategoricasCodificadas = self.Encoder.transform(VariaveisCategoricas)
            
            FeaturesCombinadas = np.hstack([tfidf_reduced, VariveisCategoricasCodificadas, VariaveisNumericasEscaladas])
            
            Distancias, Indices = self.Modelo.kneighbors(FeaturesCombinadas)
            
            informacoes_produto_base = {
                "CodigoProduto": CodigoProdutoBase,
                "Descricao": Produto['DescricaoProduto'],
                "PesoUnitario": float(Produto['PesoEmbalagemUnitaria']),
                "QtdeEmbalagem": int(Produto['QtdeEmbalagem']),
                "Secao": Produto['DescricaoSecao'],
                "Departamento": Produto['DescricaoDepartamento'],
                "Marca": Produto['Marca']
            }

            ProdutosInformacoesLista = []
            for i, CodigoProdutoRecomendado in enumerate(self.DataSet.iloc[Indices[0]]['CodigoProduto'].tolist()):
                if CodigoProdutoRecomendado != CodigoProdutoBase and Distancias[0][i] < 0.92:  # Filtragem pela distância
                    ProdutoRecomendado = self.DataSet[self.DataSet['CodigoProduto'] == CodigoProdutoRecomendado]
                    if len(ProdutoRecomendado) > 0:
                        PesoRecomendado = float(ProdutoRecomendado['PesoEmbalagemUnitaria'].values[0])
                        PesoUnitarioBase = float(Produto['PesoEmbalagemUnitaria'])
                        MargemRelativa = 0.10 * PesoUnitarioBase

                        PesoUnitarioMaximo = PesoUnitarioBase - MargemRelativa
                        PesoUnitarioMinimo = PesoUnitarioBase + MargemRelativa

                        InformacoesProduto = {
                            "CodigoProduto": CodigoProdutoRecomendado,
                            "Descricao": ProdutoRecomendado['DescricaoProduto'].values[0],
                            "PesoUnitario": PesoRecomendado,
                            "QtdeEmbalagem": int(ProdutoRecomendado['QtdeEmbalagem'].values[0]),
                            "Secao": ProdutoRecomendado['DescricaoSecao'].values[0],
                            "Departamento": ProdutoRecomendado['DescricaoDepartamento'].values[0],
                            "Marca": ProdutoRecomendado['Marca'].values[0]
                        }
                        ProdutosInformacoesLista.append(InformacoesProduto)
                        QtdeTotalRecomendacoes += 1

                        if (ProdutoRecomendado['CodDepartamento'].values[0] == CodDepartamentoProdutoBase and 
                            ProdutoRecomendado['CodSecao'].values[0] == CodSecaoProdutoBase):
                            QtdeDepartamentoESecao += 1

                        if ProdutoRecomendado['QtdeEmbalagem'].values[0] == QtdeEmbalagemProdutoBase:
                            QtdeEmbalagem += 1

                        if PesoUnitarioMaximo <= PesoRecomendado <= PesoUnitarioMinimo:
                            QtdePesoUnitario += 1

            if len(ProdutosInformacoesLista) > 0:
                TotalRecomendacoes.append({
                    "ProdutoBase": informacoes_produto_base,
                    "Recomendacoes": ProdutosInformacoesLista
                })

        if QtdeTotalRecomendacoes > 0:
            PorcentagemDepartamentoESecaoIguais = (QtdeDepartamentoESecao / QtdeTotalRecomendacoes) * 100
            PorcentagemQtdeEmbalagemIguais = (QtdeEmbalagem / QtdeTotalRecomendacoes) * 100
            PorcentagemPesoUnitarioIguais = (QtdePesoUnitario / QtdeTotalRecomendacoes) * 100
        else:
            PorcentagemDepartamentoESecaoIguais = 0.0
            PorcentagemQtdeEmbalagemIguais = 0.0
            PorcentagemPesoUnitarioIguais = 0.0
            
        JsonFinal = {"RecomendacaoProdutos":TotalRecomendacoes,"Testes":{
            "PorcentagemIguaisDepartamentoESecao": PorcentagemDepartamentoESecaoIguais,
            "PorcentagemQtdeEmbalagem": PorcentagemQtdeEmbalagemIguais,
            "PorcentagemPesoUnitarioAproximados": PorcentagemPesoUnitarioIguais
        }}
        return 200, JsonFinal