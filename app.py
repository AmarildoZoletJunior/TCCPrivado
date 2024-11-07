import datetime
from functools import wraps

import jwt
from flasgger import Swagger
from flask import Flask, jsonify, request
from flask_cors import CORS

from src.config import configuration
from src.data.database import Database
from src.repositories.ArquivoRepository import ArquivoRepository
from src.repositories.ModeloRepository import ModeloRepository
from src.repositories.UsuarioRepository import UserRepository



app = Flask(__name__)
secret = configuration.stringGeracaoJWT

def create_app():
    swagger = Swagger(app)
    CORS(app)
    data = Database()



# region Usuario
@app.route("/",methods=['GET'])
def Inicial():
    return jsonify({'Mensagem':'Seja bem vindo a API de recomendação de produtos'}), 200
    
def tokenNecessario(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        Token = None
        if 'Authorization' in request.headers:
            CabecalhoAutenticacao = request.headers['Authorization']
            if CabecalhoAutenticacao.startswith("Bearer "):
                Token = CabecalhoAutenticacao.split(" ")[1]
            else:
                return jsonify({'Erro': 'Formato do token inválido!'}), 401
        else:
            return jsonify({'Erro': 'Token é necessário!'}), 401

        try:
            Dados = jwt.decode(Token, secret, algorithms=["HS256"])
            UsuarioAtual = Dados['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({'Erro': 'Token expirado!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'Erro': 'Token inválido!'}), 401

        return f(UsuarioAtual, *args, **kwargs)

    return decorated

def criarTokenJWT(user_id):
    Token = jwt.encode({
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }, app.config['SECRET_KEY'], algorithm="HS256")
    return Token



@app.route("/login",methods=['POST'])
def EntrarNaConta():
    try:
        Dados = request.get_json(force=True)
        UserRep = UserRepository(Dados)
        Resposta, Mensagem = UserRep.ValidUser()
        if not Resposta:
            return jsonify({'Erro': Mensagem}), 400
        ListaUsuario = UserRep.FindUser()

        if ListaUsuario and isinstance(ListaUsuario, list) and len(ListaUsuario) > 0:
            Usuario = ListaUsuario[0]
            IdUsuario = Usuario.get('USUid')
            Token = criarTokenJWT(IdUsuario)

            return jsonify({
                'Mensagem': 'Usuário encontrado com sucesso',
                'token': Token
            }), 200
        else:
            return jsonify({'Erro': 'Usuário não encontrado'}), 400

    except Exception as Erro:
        return jsonify({'Erro': f'Ocorreu um erro: {Erro}'}), 500
    
    
    
    
@app.route("/criar/usuario",methods=['POST'])
def RegistrarConta():
    try:
        Dados = request.get_json(force=True)
        UserRep = UserRepository(Dados)
        Resposta,Mensagem = UserRep.CreateUser()
        if Resposta == 400:
            return jsonify({'Erro': Mensagem}), 400
        else:
            return jsonify({'Mensagem': f'Usuário cadastrado com sucesso'}), 200
    except Exception as Erro:
        return jsonify({'Erro': f'Ocorreu um erro, erro: {Erro}'}), 500
    
    
@app.route("/atualizar/senha",methods=['PUT'])
def ResetSenha():
    try:
        Dados = request.get_json(force=True)
        UserRep = UserRepository(Dados)
        Resposta,Mensagem = UserRep.ResetPassword()
        if Resposta == 400:
            return jsonify({'Erro': Mensagem}), 400
        else:
            return jsonify({'Mensagem': f'Usuário cadastrado com sucesso'}), 200
    except Exception as Erro:
        return jsonify({'Erro': f'Ocorreu um erro, erro: {Erro}'}), 500
        
# endregion                 
  
@app.route("/gerarModelo", methods=['POST'])
def GeracaoModelo():
    """
    Gerar modelo de recomendação
    ---
    tags:
      - Modelo
    parameters:
      - name: JSON
        in: body
        required: true
        schema:
            type: object
            properties:
                NúmeroPCA:
                    type: integer
                    required: true
                    description: Número de componente para normalização de matriz
                QtdeRecomendação:
                    required: true
                    type: integer
                    description: Quantidade de recomendações por produto
                IdArquivo:
                    required: true
                    type: integer
                    description: Id do arquivo
                Versão:
                    required: true
                    type: string
                    description: Versão do modelo treinado
    responses:
      200:
        description: Resultado da geração do modelo
        schema:
          type: object
          properties:
            Mensagem:
              type: string
              description: O resultado da requisição
      400:
        description: Erro ao treinar máquina
        schema:
          type: object
          properties:
            Erro:
              type: string
              description: Mensagem de erro da requisição   
      500:
        description: Erro inesperado
        schema:
          type: object
          properties:
            Erro:
              type: string
              description: Mensagem de erro da requisição, erro desconhecido.
    """
    try:
        Dados = request.get_json(force=True)
        ModeloRep = ModeloRepository(Dados)
        Resposta,Mensagem = ModeloRep.CriarModelo()
        if Resposta == 400:
            return jsonify({'Erro': Mensagem}), 400
        return jsonify({'Mensagem':'Seu modelo foi gerado com sucesso.'}), 200
    except Exception as Erro:
        return jsonify({'Erro': f'Ocorreu um erro: {Erro}'}), 500 
    
    
@app.route("/removerModelo/<int:IdModelo>", methods=['DELETE']) #OK
def RemoverModelo(IdModelo):
    """
    Deletar modelo de recomendação
    ---
    tags:
      - Modelo
    parameters:
      - name: IdModelo
        in: path
        type: integer
        required: true
        description: Id do modelo a ser removido
    responses:
      204:
        description: Modelo removido com sucesso
      404:
        description: Modelo não encontrado
        schema:
          type: object
          properties:
            error:
              type: string
              description: Mensagem de erro
      500:
        description: Erro interno do servidor
        schema:
          type: object
          properties:
            error:
              type: string
              description: Mensagem de erro
    """

    try:
        ModeloRep = ModeloRepository('')
        Resposta,Mensagem = ModeloRep.RemoverModelo(IdModelo)
        if Resposta == 400:
            return jsonify({'Erro': Mensagem}), 400
        return jsonify({'Mensagem':'Seu modelo foi removido com sucesso.'}), 200
    except Exception as Erro:
        return jsonify({'Erro': f'Ocorreu um erro: {Erro}'}), 500 
    
    
@app.route("/recomendarProdutos", methods=['POST']) #OK
def RecomendarTodosProdutosModelo():
    """
    Recomendar todos os produtos 
    ---
    tags:
      - Recomendação
    parameters:
      - name: JSON
        in: body
        required: true
        schema:
            type: object
            properties:
                Id Modelo:
                    type: integer
                    required: true
                    description: Id do modelo utilizado para fazer recomendação
    responses:
      200:
        description: Resultado da recomendação do modelo
        schema:
          type: object
          properties:
            Dados:
              type: string
              description: O resultado da requisição
      400:
        description: Erro ao treinar máquina
        schema:
          type: object
          properties:
            Erro:
              type: string
              description: Mensagem de erro da requisição   
      500:
        description: Erro inesperado
        schema:
          type: object
          properties:
            Erro:
              type: string
              description: Mensagem de erro da requisição, erro desconhecido.
    """
    try:
        data = request.get_json(force=True)
        ModeloRep = ModeloRepository(data)
        Resposta,Mensagem = ModeloRep.RecomendacaoProdutosTotal()
        if Resposta == 400:
            return jsonify({'Erro': Mensagem}), 400
        return jsonify({'Dados':Mensagem}), 200
    except Exception as Erro:
        return jsonify({'Erro': f'Ocorreu um erro: {Erro}'}), 500    
    
@app.route("/recomendarProduto", methods=['POST']) #OK
def RecomendarProdutoReferenciado():
    """
    Recomendar produtos similares a um único produto
    ---
    tags:
      - Recomendação
    parameters:
      - name: JSON
        in: body
        required: true
        schema:
            type: object
            properties:
                idModelo:
                    type: integer
                    required: true
                    description: Id do modelo utilizado para fazer recomendação
                CodigoProduto:
                    type: integer
                    required: true
                    description: Código do produto base
    responses:
      200:
        description: Resultado da recomendação do modelo
        schema:
          type: object
          properties:
            Dados:
              type: string
              description: O resultado da requisição
      400:
        description: Erro ao treinar máquina
        schema:
          type: object
          properties:
            Erro:
              type: string
              description: Mensagem de erro da requisição   
      500:
        description: Erro inesperado
        schema:
          type: object
          properties:
            Erro:
              type: string
              description: Mensagem de erro da requisição, erro desconhecido.
    """
    try:
        Dado = request.get_json(force=True)
        ModeloRep = ModeloRepository(Dado)
        Resposta,Mensagem = ModeloRep.RecomendacaoProdutoUnico()
        if Resposta == 400:
            print(Mensagem)
            return jsonify({'Erro': Mensagem}), 400
        return jsonify({'Dados':Mensagem}), 200
    except Exception as Erro:
        return jsonify({'Erro': f'Ocorreu um erro: {Erro}'}), 500    
    

  
  
  
@app.route("/cadastrarDataSet", methods=['POST']) #OK
def CadastrarDataSet():
    """
    Gerar modelo de recomendação
    ---
    tags:
      - Base de produtos
    parameters:
      - name: versao
        in: FormData
        type: integer
        required: true
        description: Versão do dataset
      - name: idUsuario
        in: FormData
        type: integer
        required: true
        description: Id do usuário
      - name: delimiter
        in: FormData
        type: integer
        required: true
        description: Delimitador para quebrar a linha
      - name: file
        in: formData
        type: file
        required: true
        description: Arquivo a ser processado (CSV, JSON)
    responses:
      200:
        description: Resultado do registro do dataset
        schema:
          type: object
          properties:
            Mensagem:
              type: string
              description: O resultado da requisição
      400:
        description: Erro ao treinar máquina
        schema:
          type: object
          properties:
            Erro:
              type: string
              description: Mensagem de erro da requisição   
      500:
        description: Erro inesperado
        schema:
          type: object
          properties:
            Erro:
              type: string
              description: Mensagem de erro da requisição, erro desconhecido.
    """
    try:
        ArquivoRepositorio = ArquivoRepository(request)
        Resposta,Mensagem = ArquivoRepositorio.RegistrarArquivo()
        if Resposta == 400:
            return jsonify({'Erro': Mensagem}), 400
        return jsonify({'Mensagem': 'Registro cadastrado com sucesso.'}), 200
    except Exception as Erro:
        return jsonify({'Erro': f'Ocorreu um erro: {Erro}'}), 500   
    
@app.route("/removerDataSet/<int:CodigoDataSet>", methods=['DELETE']) #OK
def RemoverDataSet(CodigoDataSet):
    """
    Deletar DataSet de produtos
    ---
    tags:
      - Base de produtos
    parameters:
      - name: CodigoDataSet
        in: path
        type: integer
        required: true
        description: Id do DataSet a ser removido.
    responses:
      204:
        description: DataSet removido com sucesso
      404:
        description: DataSet não encontrado
        schema:
          type: object
          properties:
            error:
              type: string
              description: Mensagem de erro
      500:
        description: Erro interno do servidor
        schema:
          type: object
          properties:
            error:
              type: string
              description: Mensagem de erro
    """
    try:
        ArquivosRep = ArquivoRepository(request)
        Resposta,Mensagem = ArquivosRep.RemoverArquivo(CodigoDataSet)
        if Resposta == 400:
            return jsonify({'Erro': Mensagem}), 400
        return jsonify({'Mensagem': 'Registro removido com sucesso.'}), 200
    except Exception as Erro:
        return jsonify({'Erro': f'Ocorreu um erro: {Erro}'}), 500   
    
@app.route("/listaDataSets", methods=['GET']) #OK
def ListaDataSets():
    """
    Lista de DataSets de produtos
    ---
    tags:
      - Base de produtos
    responses:
      200:
        description: Resultado da recomendação do modelo
        schema:
          type: object
          properties:
            Dados:
              type: string
              description: O resultado da requisição
      400:
        description: Erro ao treinar máquina
        schema:
          type: object
          properties:
            Erro:
              type: string
              description: Mensagem de erro da requisição   
      500:
        description: Erro inesperado
        schema:
          type: object
          properties:
            Erro:
              type: string
              description: Mensagem de erro da requisição, erro desconhecido.
    """
    try:
        ArquivoRep = ArquivoRepository(request)
        Resposta,Mensagem,DadosRetorno = ArquivoRep.ListarArquivos()
        if Resposta == 400:
            return jsonify({'Erro': Mensagem}), 400
        return jsonify({'Mensagem': DadosRetorno}), 200
    except Exception as Erro:
        return jsonify({'Erro': f'Ocorreu um erro: {Erro}'}), 500   
    
@app.route("/dataSet/<int:IdDataSet>", methods=['GET']) #OK
def ListarDataSet(IdDataSet):
    """
    Lista de DataSets de produtos específico
    ---
    tags:
      - Base de produtos
    parameters:
      - name: IdDataSet
        in: path
        type: integer
        required: true
        description: Id do DataSet a ser listado
    responses:
      200:
        description: Resultado da listagem de DataSets
        schema:
          type: object
          properties:
            Dados:
              type: string
              description: O resultado da requisição
      400:
        description: Erro ao treinar máquina
        schema:
          type: object
          properties:
            Erro:
              type: string
              description: Mensagem de erro da requisição   
      500:
        description: Erro inesperado
        schema:
          type: object
          properties:
            Erro:
              type: string
              description: Mensagem de erro da requisição, erro desconhecido.
    """
    try:
        ArquivoRep = ArquivoRepository(request)
        Resposta,Mensagem,DadosRetorno = ArquivoRep.ListarArquivoUnico(IdDataSet)
        if Resposta == 400:
            return jsonify({'Erro': Mensagem}), 400
        return jsonify({'Mensagem': DadosRetorno}), 200
    except Exception as Erro:
        return jsonify({'Erro': f'Ocorreu um erro: {Erro}'}), 500   
    
if __name__ == '__main__':
    create_app()
    app.run(host=configuration.ip, port=configuration.porta,debug=True)