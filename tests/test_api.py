import pytest
from unittest.mock import patch, MagicMock
from app import app


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

@pytest.fixture
def Mocks():
    with patch('src.repositories.ArquivoRepository.Database') as MockDatabaseArquivo, \
         patch('src.repositories.UsuarioRepository.Database') as MockDatabaseUsuario, \
         patch('src.repositories.ModeloRepository.Database') as MockDatabaseModelo   :
        mock_db_instance = MagicMock()
        MockDatabaseArquivo.return_value = mock_db_instance
        MockDatabaseUsuario.return_value = mock_db_instance
        MockDatabaseModelo.return_value = mock_db_instance
        yield mock_db_instance



def test_remover_dataset(Mocks, client):
    Mocks.SelecionarRegistro.return_value = [(1,'AKIOSJDIAOSJDO1IO2IKO4N12412JIO4JN1M2UIJO4')]
    Mocks.DeletarRegistro.return_value = True

    response = client.delete('/removerDataSet/1')  # ID do dataset a ser removido
    
    assert response.status_code == 200
    json_data = response.get_json()
    assert 'Mensagem' in json_data
    assert json_data['Mensagem'] == 'Registro removido com sucesso.'


def test_remover_dataset_nao_encontrado(Mocks, client):
    Mocks.SelecionarRegistro.return_value = []

    response = client.delete('/removerDataSet/9999') 
    
    assert response.status_code == 400
    json_data = response.get_json()
    assert 'Erro' in json_data
    assert json_data['Erro'] == 'Não foi encontrado o arquivo com o id:9999'

def test_listar_datasets(Mocks, client):
    Mocks.SelecionarRegistro.return_value = [{'APId': 1, 'Nome': 'Dataset1'}, {'APId': 2, 'Nome': 'Dataset2'}]

    response = client.get('/listaDataSets')
    
    assert response.status_code == 200
    json_data = response.get_json()
    assert 'Mensagem' in json_data
    assert len(json_data['Mensagem']) == 2 


def test_listar_datasets_erro(Mocks, client):
    Mocks.SelecionarRegistro.return_value = []

    response = client.get('/listaDataSets')
    
    assert response.status_code == 400
    json_data = response.get_json()
    assert 'Erro' in json_data
    assert json_data['Erro'] == 'Não foi encontrado nenhum arquivo.'

def test_listar_dataset_especifico(Mocks, client):
    Mocks.SelecionarRegistro.return_value = [{'APId': 1, 'Nome': 'Dataset1'}]

    response = client.get('/dataSet/1')
    
    assert response.status_code == 200
    json_data = response.get_json()
    assert 'Mensagem' in json_data
    assert len(json_data['Mensagem']) == 1
    assert json_data['Mensagem'][0]['APId'] == 1

def test_listar_dataset_especifico_erro(Mocks, client):
    Mocks.SelecionarRegistro.return_value = []

    response = client.get('/dataSet/9999')
    
    assert response.status_code == 400
    json_data = response.get_json()
    assert 'Erro' in json_data
    assert json_data['Erro'] == 'Não foi encontrado nenhum arquivo.'
    
    
    
def test_remover_modelo_erro(Mocks, client):
    Mocks.SelecionarRegistro.return_value = []


    response = client.delete('/removerModelo/1')
    
    assert response.status_code == 400
    json_data = response.get_json()
    assert 'Erro' in json_data
    assert json_data['Erro'] == 'Não foi encontrado o registro do modelo, Id: 1'


def test_remover_modelo(Mocks, client):
    Mocks.SelecionarRegistro.return_value = [(1,'modelotal')]


    response = client.delete('/removerModelo/1')
    
    assert response.status_code == 200
    json_data = response.get_json()
    assert 'Mensagem' in json_data
    assert json_data['Mensagem'] == 'Seu modelo foi removido com sucesso.'
    
    
def test_gerarModelo_modelo_erro_falta_parametro_qtdeRecomendacao(Mocks, client):

    data = {
        'idArquivo':1,
        'versao':'v1.0',
        'idUsuario':2,
        'numPca':400,
        # 'qtdeRecomendacao':2
    }
    response = client.post('/gerarModelo', json=data)
    
    assert response.status_code == 400
    json_data = response.get_json()
    assert 'Erro' in json_data
    assert json_data['Erro'] == 'Parâmetro qtdeRecomendacao é obrigatório.'
    
    
def test_gerarModelo_modelo_erro_falta_parametro_numPca(Mocks, client):

    data = {
        'idArquivo':1,
        'versao':'v1.0',
        'idUsuario':2,
        # 'numPca':400,
        'qtdeRecomendacao':2
    }
    response = client.post('/gerarModelo', json=data)
    
    assert response.status_code == 400
    json_data = response.get_json()
    assert 'Erro' in json_data
    assert json_data['Erro'] == 'Parâmetro numPca é obrigatório.'
    
    
def test_gerarModelo_modelo_erro_falta_parametro_idUsuario(Mocks, client):

    data = {
        'idArquivo':1,
        'versao':'v1.0',
        # 'idUsuario':2,
        'numPca':400,
        'qtdeRecomendacao':2
    }
    response = client.post('/gerarModelo', json=data)
    
    assert response.status_code == 400
    json_data = response.get_json()
    assert 'Erro' in json_data
    assert json_data['Erro'] == 'Parâmetro IdUsuario é obrigatório.'
    
def test_gerarModelo_modelo_erro_falta_parametro_versao(Mocks, client):

    data = {
        'idArquivo':1,
        # 'versao':'v1.0',
        'idUsuario':2,
        'numPca':400,
        'qtdeRecomendacao':2
    }
    response = client.post('/gerarModelo', json=data)
    
    assert response.status_code == 400
    json_data = response.get_json()
    assert 'Erro' in json_data
    assert json_data['Erro'] == 'Parâmetro versao é obrigatório.'
    
    
def test_gerarModelo_modelo_erro_falta_parametro_idArquivo(Mocks, client):

    data = {
        # 'idArquivo':1,
        'versao':'v1.0',
        'idUsuario':2,
        'numPca':400,
        'qtdeRecomendacao':2
    }
    response = client.post('/gerarModelo', json=data)
    
    assert response.status_code == 400
    json_data = response.get_json()
    assert 'Erro' in json_data
    assert json_data['Erro'] == 'Parâmetro idArquivo é obrigatório.'
    
    





def test_gerarModelo_modelo_erro_falta_parametro_idArquivo_naoInteiro(Mocks, client):

    data = {
        'idArquivo':'1',
        'versao':'v1.0',
        'idUsuario':2,
        'numPca':400,
        'qtdeRecomendacao':2
    }
    response = client.post('/gerarModelo', json=data)
    
    assert response.status_code == 400
    json_data = response.get_json()
    assert 'Erro' in json_data
    assert json_data['Erro'] == 'Parâmetro idArquivo pode ser apenas do tipo inteiro'


def test_gerarModelo_modelo_erro_falta_parametro_versao_naoString(Mocks, client):

    data = {
        'idArquivo':1,
        'versao':1.0,
        'idUsuario':2,
        'numPca':400,
        'qtdeRecomendacao':2
    }
    response = client.post('/gerarModelo', json=data)
    
    assert response.status_code == 400
    json_data = response.get_json()
    assert 'Erro' in json_data
    assert json_data['Erro'] == 'Parâmetro versao pode ser apenas texto.'
    
    
def test_gerarModelo_modelo_erro_falta_parametro_versao_naoString(Mocks, client):

    data = {
        'idArquivo':1,
        'versao':1.0,
        'idUsuario':2,
        'numPca':400,
        'qtdeRecomendacao':2
    }
    response = client.post('/gerarModelo', json=data)
    
    assert response.status_code == 400
    json_data = response.get_json()
    assert 'Erro' in json_data
    assert json_data['Erro'] == 'Parâmetro versao pode ser apenas texto.'