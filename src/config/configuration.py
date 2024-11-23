import os
from configparser import ConfigParser
from time import sleep

config_file = r'./src/config/config.ini'

def EncontrarValorVariaveis(Valor):
    while "${" in Valor:
        IndiceInicial = Valor.find("${") + 2
        IndiceFinal = Valor.find("}", IndiceInicial)
        NomeVariavel = Valor[IndiceInicial:IndiceFinal]
        ValorPadrao = None
        if ":" in NomeVariavel:
            NomeVariavel, ValorPadrao = NomeVariavel.split(":", 1)
        ValorAmbiente = os.getenv(NomeVariavel, ValorPadrao)
        Valor = ValorAmbiente
    return Valor

conf_obj = ConfigParser()

if os.path.exists(config_file):
    conf_obj.read(config_file)
else:
    raise FileNotFoundError(f"Arquivo de configuração não encontrado: {config_file}")

try:
    if 'DataBase' in conf_obj:
        config = conf_obj['DataBase']
        DRIVER = EncontrarValorVariaveis(config.get('DRIVER', None))
        SERVER = EncontrarValorVariaveis(config.get('SERVER', None))
        DATABASE = EncontrarValorVariaveis(config.get('DATABASE', None))

        if DRIVER is None or SERVER is None or DATABASE is None:
            raise ValueError("Alguma chave está faltando na seção [DataBase].")

    if 'Parametros' in conf_obj:
        config = conf_obj['Parametros']
        ip = EncontrarValorVariaveis(config.get('ip', None))
        porta = EncontrarValorVariaveis(config.get('porta', None))
        stringGeracaoJWT = EncontrarValorVariaveis(config.get('StringCodificacaoJWT', None))

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
