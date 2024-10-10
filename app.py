import io
import pandas as pd
from flask import Flask, request, jsonify, make_response
from entidades.dados import ManipulacaoCSV
from entidades.KNN import AlgoritmoKNN

app = Flask(__name__)

@app.route("/welcome",methods=['GET'])
def Inicial():
    print("Teste")

    
@app.route("/treinamentoRapido", methods=['POST'])
def treinamento():
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

        if not num_pca or not qtde_recomendacao:
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
        KNN.treinamentoKNN()
        recomendacao = KNN.recomendarTodosProdutos()

        return jsonify({'Mensagem':recomendacao}), 200
    except Exception as error:
        return jsonify({'Erro': f'Ocorreu um erro: {error}'}), 500

