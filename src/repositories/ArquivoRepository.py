import io

import pandas as pd

from src.data.database import Database
from src.entidades.arquivos import Arquivos


class ArquivoRepository():
    def __init__(self,request):
        self.Requisicao = request
        self.ColunasVerificacao = [
            'codprod',
            'descricaoproduto',
            'embalagem',
            'unidade',
            'codepto',
            'deptodescricao',
            'codsec',
            'secdescricao',
            'codncmex',
            'nbm',
            'informacoestecnicas',
            'codmarca',
            'marca',
            'codmarcatabelamarcas',
            'marcatabelamarcas',
        ]
        
        
    def VerificarArquivo(self,Delimitador,IdUsuario,Versao):
        if 'file' not in self.Requisicao.files:
            return False,'Nenhum arquivo enviado.'
        
        Arquivo = self.Requisicao.files['file']
        if Arquivo.filename == '':
            return False, 'Nenhum nome de arquivo enviado.'
        
        if not Arquivo.filename.endswith('.csv'):
            return False,'O arquivo não é CSV.'
        
        
        if not Delimitador:
            return False,'Parâmetro delimiter é obrigatório'
        
        if len(Delimitador) == 0:
            return False,'Parâmetro delimiter é obrigatório'
        
        
        if not IdUsuario:
            return False,'Parâmetro idUsuario é obrigatório'
        
        if not Versao:
            return False,'Parâmetro versao é obrigatório'
        
        self.ArquivoConteudo  = Arquivo.stream.read()
        
        try:
            self.DataSet = pd.read_csv(io.StringIO(self.ArquivoConteudo.decode('ISO-8859-1')), delimiter=Delimitador)
        except pd.errors.ParserError as Erro:
            return False, f"Erro ao processar o arquivo CSV, verifique o delimitador"
        
        if len(self.DataSet) < 4:
            return False, 'O arquivo não contém os registros mínimos necessários que são 4.'
        
        ColunasDataSet = self.DataSet.columns.tolist()
        ColunasFaltantes = [col for col in self.ColunasVerificacao if col not in ColunasDataSet]
        if ColunasFaltantes:
            return False,f'Existem colunas faltantes no CSV, colunas: {ColunasFaltantes}'
        return True,''
        
    def RegistrarArquivo(self):
        Versao = self.Requisicao.form.get('versao')
        IdUsuario = self.Requisicao.form.get('idUsuario')
        Delimitador = self.Requisicao.form.get('delimiter')
        
        Resposta,Mensagem = self.VerificarArquivo(Delimitador,IdUsuario,Versao)
        if not Resposta:
            return 400,Mensagem
        
        ConteudoCSVTexto = self.DataSet.to_csv(index=False, sep=';')
        ConteudoCSVBinario = ConteudoCSVTexto.encode('ISO-8859-1')
        
        BaseDados = Database()
        Resposta = BaseDados.Insercao(Arquivos,APArquivo = ConteudoCSVBinario,APArquivoDelimiter = Delimitador,APQtdeProdutos = len(self.DataSet),APIdUsuario = IdUsuario,APVersao = Versao)
        if Resposta is None:
            return 400,'Ocorreu um erro ao inserir o registro.'
        return 200,''
    
    
    def RemoverArquivo(self,IdArquivo):
        if not IdArquivo:
            return 400,'Não foi encontrado o Id do arquivo.'
        if not isinstance(IdArquivo,int):
            return 400,'o id do arquivo deve ser do tipo inteiro.'
        BaseDados = Database()
        RegistrosArquivos = BaseDados.SelecionarRegistro(Arquivos,APId = IdArquivo)
        if len(RegistrosArquivos) == 0:
            return 400,f'Não foi encontrado o arquivo com o id:{IdArquivo}'
        Resposta = BaseDados.DeletarRegistro(Arquivos,APId = IdArquivo)
        if Resposta is None:
            return 400,'Ocorreu um erro ao deletar o registro.'
        return 200,''
        
    def ListarArquivos(self):
        BaseDados = Database()
        RegistrosArquivos = BaseDados.SelecionarRegistro(Arquivos)
        if len(RegistrosArquivos) == 0:
            return 400,f'Não foi encontrado nenhum arquivo.',''
        return 200,'',RegistrosArquivos
    
    def ListarArquivoUnico(self,idArquivo):
        BaseDados = Database()
        RegistrosArquivos = BaseDados.SelecionarRegistro(Arquivos,APId = idArquivo)
        if len(RegistrosArquivos) == 0:
            return 400,f'Não foi encontrado nenhum arquivo.',''
        return 200,'',RegistrosArquivos