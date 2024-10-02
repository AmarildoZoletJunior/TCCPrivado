from flask import Flask, request, jsonify, make_response

app = Flask(__name__)

@app.route("/welcome",methods=['GET'])
def Inicial():
    print("Teste")




@app.route("/treinamento",methods=['POST'])
def treinamento():
    data = request.get_json(force=True)
    print("Teste")