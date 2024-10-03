from flask import Flask, request, jsonify, make_response
from entidades.dados import ManipulacaoCSV

app = Flask(__name__)

@app.route("/welcome",methods=['GET'])
def Inicial():
    print("Teste")




@app.route("/treinamento",methods=['GET'])
def treinamento():
    try:
        Manipulacao = ManipulacaoCSV()
        Manipulacao.tratamentoCSV()
        return jsonify({'Mensagem':'Deu certo'}), 200
    except Exception as error:
        return jsonify({'Erro': f'Ocorreu um erro, erro: {error}'}), 500