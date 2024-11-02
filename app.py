import io
import pandas as pd
from src.data.database import Database
from flask import Flask, request, jsonify
from src.repositories.ArquivoRepository import ArquivoRepository
from src.repositories.ModeloRepository import ModeloRepository
from src.repositories.UsuarioRepository import UserRepository
from src.config import  configuration
import jwt
from functools import wraps
import datetime
from flask_cors import CORS 

from flasgger import Swagger




data = Database()
app = Flask(__name__)
swagger = Swagger(app)
CORS(app)

secret = '1111'

# region Usuario
@app.route("/welcome",methods=['GET'])
def Inicial():
    print("Teste")
    
def tokenNecessario(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
            else:
                return jsonify({'Erro': 'Formato do token inválido!'}), 401
        else:
            return jsonify({'Erro': 'Token é necessário!'}), 401

        try:
            data = jwt.decode(token, secret, algorithms=["HS256"])
            current_user = data['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({'Erro': 'Token expirado!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'Erro': 'Token inválido!'}), 401

        return f(current_user, *args, **kwargs)

    return decorated

def criarTokenJWT(user_id):
    token = jwt.encode({
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }, app.config['SECRET_KEY'], algorithm="HS256")
    return token



@app.route("/login",methods=['POST'])
def SignInAccount():
    try:
        data = request.get_json(force=True)
        UserRep = UserRepository(data)
        response, message = UserRep.ValidUser()
        if not response:
            return jsonify({'Erro': message}), 400
        user_list = UserRep.FindUser()

        if user_list and isinstance(user_list, list) and len(user_list) > 0:
            user = user_list[0]
            user_id = user.get('USUid')
            token = criarTokenJWT(user_id)

            return jsonify({
                'Mensagem': 'Usuário encontrado com sucesso',
                'token': token
            }), 200
        else:
            return jsonify({'Erro': 'Usuário não encontrado'}), 400

    except Exception as e:
        return jsonify({'Erro': f'Ocorreu um erro: {e}'}), 500
    
    
    
    
@app.route("/criar/usuario",methods=['POST'])
def RegisterAccount():
    try:
        data = request.get_json(force=True)
        UserRep = UserRepository(data)
        response,message = UserRep.CreateUser()
        if response == 400:
            return jsonify({'Erro': message}), 400
        else:
            return jsonify({'Mensagem': f'Usuário cadastrado com sucesso'}), 200
    except Exception as e:
        return jsonify({'Erro': f'Ocorreu um erro, erro: {e}'}), 500
    
    
@app.route("/atualizar/senha",methods=['PUT'])
def ResetPassword():
    try:
        data = request.get_json(force=True)
        UserRep = UserRepository(data)
        response,message = UserRep.ResetPassword()
        if response == 400:
            return jsonify({'Erro': message}), 400
        else:
            return jsonify({'Mensagem': f'Usuário cadastrado com sucesso'}), 200
    except Exception as e:
        return jsonify({'Erro': f'Ocorreu um erro, erro: {e}'}), 500
        
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
        data = request.get_json(force=True)
        ModeloRep = ModeloRepository(data)
        response,message = ModeloRep.CriarModelo()
        if response == 400:
            return jsonify({'Erro': message}), 400
        return jsonify({'Mensagem':'Seu modelo foi gerado com sucesso.'}), 200
    except Exception as error:
        return jsonify({'Erro': f'Ocorreu um erro: {error}'}), 500 
    
    
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
        response,message = ModeloRep.RemoverModelo(IdModelo)
        if response == 400:
            return jsonify({'Erro': message}), 400
        return jsonify({'Mensagem':'Seu modelo foi gerado com sucesso.'}), 200
    except Exception as error:
        return jsonify({'Erro': f'Ocorreu um erro: {error}'}), 500 
    
    
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
        response,message = ModeloRep.RecomendacaoProdutosTotal()
        if response == 400:
            return jsonify({'Erro': message}), 400
        return jsonify({'Dados':message}), 200
    except Exception as error:
        return jsonify({'Erro': f'Ocorreu um erro: {error}'}), 500    
    
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
        data = request.get_json(force=True)
        ModeloRep = ModeloRepository(data)
        response,message = ModeloRep.RecomendacaoProdutoUnico()
        if response == 400:
            print(message)
            return jsonify({'Erro': message}), 400
        return jsonify({'Dados':message}), 200
    except Exception as error:
        return jsonify({'Erro': f'Ocorreu um erro: {error}'}), 500    
    

  
  
  
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
        response,message = ArquivoRepositorio.RegistrarArquivo()
        if response == 400:
            return jsonify({'Erro': message}), 400
        return jsonify({'Mensagem': 'Registro cadastrado com sucesso.'}), 200
    except Exception as error:
        return jsonify({'Erro': f'Ocorreu um erro: {error}'}), 500   
    
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
        ArquivoRepositorio = ArquivoRepository(request)
        response,message = ArquivoRepositorio.RemoverArquivo(CodigoDataSet)
        if response == 400:
            return jsonify({'Erro': message}), 400
        return jsonify({'Mensagem': 'Registro removido com sucesso.'}), 200
    except Exception as error:
        return jsonify({'Erro': f'Ocorreu um erro: {error}'}), 500   
    
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
        ArquivoRepositorio = ArquivoRepository(request)
        response,message,data = ArquivoRepositorio.ListarArquivos()
        if response == 400:
            return jsonify({'Erro': message}), 400
        return jsonify({'Mensagem': data}), 200
    except Exception as error:
        return jsonify({'Erro': f'Ocorreu um erro: {error}'}), 500   
    
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
        ArquivoRepositorio = ArquivoRepository(request)
        response,message,data = ArquivoRepositorio.ListarArquivoUnico(IdDataSet)
        if response == 400:
            return jsonify({'Erro': message}), 400
        return jsonify({'Mensagem': data}), 200
    except Exception as error:
        return jsonify({'Erro': f'Ocorreu um erro: {error}'}), 500   
    
if __name__ == '__main__':
    app.run(host=configuration.ip, port=configuration.porta)