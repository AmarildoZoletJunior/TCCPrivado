import io
import pandas as pd
from src.data.database import Database
from flask import Flask, request, jsonify
from src.repositories.ArquivoRepository import ArquivoRepository
from src.repositories.ModeloRepository import ModeloRepository
from src.repositories.UsuarioRepository import UserRepository

from src.entidades.tratamentoDados import ManipulacaoCSV
from src.entidades.treinamentos import AlgoritmoKNN
from src.config import  configuration
import jwt
from functools import wraps
import datetime




data = Database()
app = Flask(__name__)

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
        
# region EndPointAntigo

    
@app.route("/treinamentoAlgoritmo", methods=['POST'])
def Treinamento():
    try:
        if 'file' not in request.files:
            return jsonify({'Erro': 'Nenhum arquivo enviado'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'Erro': 'Nenhum nome de arquivo enviado'}), 400
        if not file.filename.endswith('.csv'):
            return jsonify({'Erro': 'O arquivo não é CSV'}), 400

        csv_data = pd.read_csv(io.StringIO(file.stream.read().decode('ISO-8859-1')), delimiter=';')
        num_pca = request.form.get('NumPca')
        qtde_recomendacao = request.form.get('QtdeRecomendacao')
        
        if not num_pca:
            return jsonify({'Erro': 'Parâmetro NumPca é obrigatórios'}), 400
        
        if not qtde_recomendacao:
            return jsonify({'Erro': 'Parâmetro QtdeRecomendacao é obrigatórios'}), 400

        if len(csv_data) < int(num_pca):
            return jsonify({'Erro':f'O número de componente deve ser menor ou igual a quantidade de registros, quantidade de registros do CSV é: {len(csv_data)}'})


        try:
            num_pca = int(num_pca)
            qtde_recomendacao = int(qtde_recomendacao)
        except ValueError:
            return jsonify({'Erro': 'NumPca e QtdeRecomendacao devem ser números inteiros'}), 400
        
        ManipulacaoDados = ManipulacaoCSV(csv_data)
        response, message = ManipulacaoDados.validarDadosCSV()
        if not response:
            return jsonify({'Mensagem': message}), 400

        response, message, dataSet = ManipulacaoDados.tratamentoCSV()
        if not response:
            return jsonify({'Mensagem': message}), 400
        
        KNN = AlgoritmoKNN(dataSet, num_pca, qtde_recomendacao)
        response,message = KNN.treinamentoKNN()
        
        if response == 400:
            return jsonify({'Erro': f'Ocorreu um erro: {message}'}), response
        return jsonify({'Mensagem':'Seu algoritmo foi treinado com sucesso.'}), 200
    except Exception as error:
        return jsonify({'Erro': f'Ocorreu um erro: {error}'}), 500



@app.route("/recomendacaoItem/<int:CodigoProduto>", methods=['GET'])
def RecomendacaoItem(CodigoProduto):
    try:
        recomendador = AlgoritmoKNN('','','')
        status, resultado = recomendador.RecomendarProdutosPorCodigo(CodigoProduto)
        if status == 200:
            return jsonify({'ProdutosRecomendados': resultado}), 200
        else:
            return jsonify({'Erro': resultado}), 400
    except Exception as error:
        return jsonify({'Erro': f'Ocorreu um erro: {error}'}), 500




@app.route("/recomendacaoTodosItens", methods=['GET'])
def RecomendacaoTodosItens():
    try:
        recomendador = AlgoritmoKNN('','','')
        status, resultado,porcentagem_iguais = recomendador.RecomendarTodosProdutos()
        if status == 200:
            return jsonify({'PorcAcertoSecaoDepto':porcentagem_iguais,'ProdutosRecomendados': resultado}), 200
        else:
            return jsonify({'Erro': resultado}), 400
    except Exception as error:
        return jsonify({'Erro': f'Ocorreu um erro: {error}'}), 500
    
    
# endregion
  
@app.route("/gerarModelo", methods=['POST'])
def GeracaoModelo():
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
    try:
        ModeloRep = ModeloRepository('')
        response,message = ModeloRep.RemoverModelo(IdModelo)
        if response == 400:
            return jsonify({'Erro': message}), 400
        return jsonify({'Mensagem':'Seu modelo foi gerado com sucesso.'}), 200
    except Exception as error:
        return jsonify({'Erro': f'Ocorreu um erro: {error}'}), 500 
    
    
@app.route("/recomendarProdutos", methods=['GET']) #OK
def RecomendarTodosProdutosModelo():
    try:
        data = request.get_json(force=True)
        ModeloRep = ModeloRepository(data)
        response,message = ModeloRep.RecomendacaoProdutosTotal()
        if response == 400:
            return jsonify({'Erro': message}), 400
        return jsonify({'Dados':message}), 200
    except Exception as error:
        return jsonify({'Erro': f'Ocorreu um erro: {error}'}), 500    
    
@app.route("/recomendarProduto", methods=['GET']) #OK
def RecomendarProdutoReferenciado():
    try:
        data = request.get_json(force=True)
        ModeloRep = ModeloRepository(data)
        response,message = ModeloRep.RecomendacaoProdutoUnico()
        if response == 400:
            return jsonify({'Erro': message}), 400
        return jsonify({'Dados':message}), 200
    except Exception as error:
        return jsonify({'Erro': f'Ocorreu um erro: {error}'}), 500    
    

  
  
  
@app.route("/cadastrarDataSet", methods=['POST']) #OK
def CadastrarDataSet():
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