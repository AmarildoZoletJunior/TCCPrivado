from configparser import ConfigParser
import os

# Caminho absoluto para o arquivo de configuração
config_file = r'C:\Users\amjun\Desktop\Catolica\TCC\TCCPrivado\src\config\config.ini'

# Inicializa o ConfigParser
conf_obj = ConfigParser()

# Verifica se o arquivo existe
if os.path.exists(config_file):
    conf_obj.read(config_file)
else:
    raise FileNotFoundError(f"Arquivo de configuração não encontrado: {config_file}")

try:
    
    # Acessando a seção 'DataBase'
    if 'DataBase' in conf_obj:
        config = conf_obj['DataBase']
        DRIVER = config.get('DRIVER', None)
        SERVER = config.get('SERVER', None)
        DATABASE = config.get('DATABASE', None)

        # Verifica se as chaves foram corretamente obtidas
        if DRIVER is None or SERVER is None or DATABASE is None:
            raise ValueError("Alguma chave está faltando na seção [DataBase].")
        
    # Acessando a seção 'Parametros'
    if 'Parametros' in conf_obj:
        config = conf_obj['Parametros']
        UrlPastaModelos = config.get('UrlPastaModelos', None)
        UrlPastaParametros = config.get('UrlPastaParametros', None)
        UrlPastaDataSet = config.get('UrlPastaDataSet', None)
        ip = config.get('ip', None)
        porta = config.get('porta', None)
        
        if UrlPastaModelos is None:
            raise ValueError("Chave 'UrlPastaModelos' não encontrada na seção [Parametros].")
        
        if UrlPastaParametros is None:
            raise ValueError("Chave 'UrlPastaParametros' não encontrada na seção [Parametros].")
        
        if UrlPastaDataSet is None:
            raise ValueError("Chave 'UrlPastaDataSet' não encontrada na seção [Parametros].")
        
        if ip is None:
            raise ValueError("Chave 'ip' não encontrada na seção [Parametros].")

        if porta is None:
            raise ValueError("Chave 'porta' não encontrada na seção [Parametros].")
    else:
        raise ValueError("Seção 'Parametros' não encontrada no arquivo de configuração.")


except Exception as e:
    print(f"Erro ao ler o arquivo de configuração: {e}")
