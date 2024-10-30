import io
from src.entidades.arquivos import Arquivos
from src.data.database import Database
import pandas as pd


class ArquivoRepository():
    def __init__(self,request):
        self.request = request
        self.colunasVerificacao = [
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
        
        
    def VerificarArquivo(self,delimiter,idUsuario,versao):
        if 'file' not in self.request.files:
            return False,'Nenhum arquivo enviado.'
        
        arquivo = self.request.files['file']
        if arquivo.filename == '':
            return False, 'Nenhum nome de arquivo enviado.'
        
        if not arquivo.filename.endswith('.csv'):
            return False,'O arquivo não é CSV.'
        
        
        if not delimiter:
            return False,'Parâmetro delimiter é obrigatório'
        
        if len(delimiter) == 0:
            return False,'Parâmetro delimiter é obrigatório'
        
        
        if not idUsuario:
            return False,'Parâmetro idUsuario é obrigatório'
        
        if not versao:
            return False,'Parâmetro versao é obrigatório'
        
        self.file_content  = arquivo.stream.read()
        
        try:
            self.DataSet = pd.read_csv(io.StringIO(self.file_content.decode('ISO-8859-1')), delimiter=delimiter)
        except pd.errors.ParserError as e:
            return False, f"Erro ao processar o arquivo CSV, verifique o delimitador"
        
        if len(self.DataSet) < 4:
            return False, 'O arquivo não contém os registros mínimos necessários que são 4.'
        
        colunasDataset = self.DataSet.columns.tolist()
        colunasFaltantes = [col for col in self.colunasVerificacao if col not in colunasDataset]
        if colunasFaltantes:
            return False,f'Existem colunas faltantes no CSV, colunas: {colunasFaltantes}'
        return True,''
        
    def RegistrarArquivo(self):
        versao = self.request.form.get('versao')
        idUsuario = self.request.form.get('idUsuario')
        delimiter = self.request.form.get('delimiter')
        response,message = self.VerificarArquivo(delimiter,idUsuario,versao)
        
        if not response:
            return 400,message
        
        csv_content_str = self.DataSet.to_csv(index=False, sep=';')
        csv_content_binary = csv_content_str.encode('ISO-8859-1')
        
        data = Database()
        response = data.DoInsert(Arquivos,APArquivo = csv_content_binary,APArquivoDelimiter = delimiter,APQtdeProdutos = len(self.DataSet),APIdUsuario = idUsuario,APVersao = versao)
        if response is None:
            return 400,'Ocorreu um erro ao inserir o registro.'
        return 200,''
    
    
    def RemoverArquivo(self,idArquivo):
        if not idArquivo:
            return 400,'Não foi encontrado o Id do arquivo.'
        if not isinstance(idArquivo,int):
            return 400,'o id do arquivo deve ser do tipo inteiro.'
        dataBase = Database()
        data = dataBase.DoSelect(Arquivos,APId = idArquivo)
        if len(data) == 0:
            return 400,f'Não foi encontrado o arquivo com o id:{idArquivo}'
        response = dataBase.DoDelete(Arquivos,APId = idArquivo)
        if response is None:
            return 400,'Ocorreu um erro ao deletar o registro.'
        return 200,''
        
    def ListarArquivos(self):
        dataBase = Database()
        data = dataBase.DoSelect(Arquivos)
        if len(data) == 0:
            return 400,f'Não foi encontrado nenhum arquivo.',''
        return 200,'',data
    
    def ListarArquivoUnico(self,idArquivo):
        dataBase = Database()
        data = dataBase.DoSelect(Arquivos,APId = idArquivo)
        if len(data) == 0:
            return 400,f'Não foi encontrado nenhum arquivo.',''
        return 200,'',data