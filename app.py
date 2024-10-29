import io
import os
import pandas as pd
from flask import Flask, request, jsonify
from entidades.tratamentoDados import ManipulacaoCSV
from entidades.treinamento import AlgoritmoKNN
from config import  configuration

app = Flask(__name__)

@app.route("/welcome",methods=['GET'])
def Inicial():
    print("Teste")

    
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
    
    
if __name__ == '__main__':
    app.run(host=configuration.ip, port=configuration.porta)