import os
from configparser import ConfigParser

config_file = r'./src/config/config.ini'
# config_file = r'<Letra do Disco>:\<NomeDaPastaDeUsuarios>\<NomeDoUsuario>\Desktop\<NomeDaPasta>\TCCPrivado\src\config\config.ini
# config_file = r'config.ini'


conf_obj = ConfigParser()

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
        ip = config.get('ip', None)
        porta = config.get('porta', None)
        stringGeracaoJWT = config.get('StringCodificacaoJWT',None)
        
        
        if ip is None:
            raise ValueError("Chave 'ip' não encontrada na seção [Parametros].")

        if porta is None:
            raise ValueError("Chave 'porta' não encontrada na seção [Parametros].")
    
        if stringGeracaoJWT is None:
            raise ValueError("Chave 'stringGeracaoJWT' não encontrada na seção [Parametros].")
    else:
        raise ValueError("Seção 'Parametros' não encontrada no arquivo de configuração.")


except Exception as e:
    print(f"Erro ao ler o arquivo de configuração: {e}")
