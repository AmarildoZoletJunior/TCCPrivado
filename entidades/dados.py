import re
import pandas as pd

class DadosCSV():
        def __init__(self):
            print("")
            self.mapeamentoUnidade = {
                'FD': 1,
                'UN': 2,
                'CX': 3,
                'CT': 5,
                'TR': 6,
                'PT': 7,
                'BD': 8,
                'DP': 9,
                'PK': 10,
                'KT': 11,
                'PR': 12,
                'SC': 13,
                'CJ': 14,
                'LT': 15,
                'KG': 16,
                'BJ': 17,
                'DZ': 18,
                'PC': 19
            }
            self.mapeamentoNomesColunas = {
                'codprod': 'CodigoProduto',
                'descricaoproduto': 'DescricaoProduto',
                'embalagem': 'TipoEmbalagem',
                'CodUnidade': 'CodUnidade',
                'unidade': 'Unidade',
                'codmarca': 'CodMarca',
                'marca': 'Marca',
                'codepto': 'CodDepartamento',
                'descricao':'DescricaoDepartamento',
                'codsec': 'CodSecao',
                'descricao.1': 'DescricaoSecao',
                'informacoestecnicas': 'InformacoesTecnicasV1',
                'descricao1': 'InformacoesTecnicasV2',
            }
        
        def validarDadosCSV(self):
            print()

        def tratamentoCSV(self):
            print()
            # DataSet = pd.read_csv(UrlArquivoOriginal,sep=';',encoding='latin')
            # DataSet['codmarca'].replace([np.inf, -np.inf], 9999, inplace=True)
            # DataSet['codmarca'].fillna(0, inplace=True)
            # DataSet['codmarca'] = DataSet['codmarca'].astype(int)


            # DataSet['marca'] = DataSet['marca'].str.strip().str.upper()
            # DataSet['marcatabelamarcas'] = DataSet['marcatabelamarcas'].str.strip().str.upper()
            # condicao = (DataSet['marcatabelamarcas'].notna()) & \
            #         (DataSet['marcatabelamarcas'] != '') & \
            #         (DataSet['marca'] != '0')  & \
            #         (DataSet['marca'] != DataSet['marcatabelamarcas'])

            # DataSet.loc[condicao, 'marca'] = DataSet.loc[condicao, 'marcatabelamarcas']

            # #Popular nova coluna
            # DataSet['CodUnidade'] = DataSet['unidade'].map(self.mapeamentoUnidade)

            # # Retirar colunas que não são úteis
            # DataSet = DataSet.drop(columns={'nbm','codmarcatabelamarcas','marcatabelamarcas','codauxiliar','codauxiliar','codauxiliar2','codncmex','aceitavendafracao'})

            # DataSet.rename(columns=self.mapeamentoNomesColunas, inplace=True)
            # DataSet = DataSet[['CodigoProduto', 'DescricaoProduto', 'CodMarca',
            #     'Marca' ,'TipoEmbalagem', 'CodUnidade','Unidade', 'CodDepartamento', 'DescricaoDepartamento', 'CodSecao', 'DescricaoSecao',
            #     'InformacoesTecnicasV1', 'InformacoesTecnicasV2']]



        def mudarCodMarcaSemRegistro(DataSet,Palavra,codMarca,campoFiltro):
            DataSet.loc[DataSet[campoFiltro].str.contains(fr'\b{Palavra}\b',case=False, regex=True) & (DataSet['CodMarca'] == 0), 'CodMarca'] = codMarca

        def mudarMarcaSemRegistro(DataSet,Palavra,Marca,campoFiltro):
            DataSet.loc[DataSet[campoFiltro].str.contains(rf'\b{Palavra}\b',case=False, regex=True) & (DataSet['CodMarca'] == 0), 'Marca'] = Marca

        def mudarCodMarcaJaRegistrada(Data,Palavra,codMarca,campoFiltro):
            Data.loc[Data[campoFiltro].str.contains(rf'\b{Palavra}\b',case=False, regex=True), 'CodMarca'] = codMarca

        def mudarMarcaJaRegistrada(Data,Palavra,Marca,campoFiltro):
            Data.loc[Data[campoFiltro].str.contains(rf'\b{Palavra}\b',case=False, regex=True), 'Marca'] = Marca

        def removerLinhaPorCodProduto(DataSet,CodigoProduto):
            DataSet.drop(DataSet[DataSet['CodigoProduto'] == CodigoProduto].index, inplace = True)

        def removerMarcasDescricao(descricao, marcas):
            marcas = marcas.split(',')
            for marca in marcas:
                descricao = descricao.replace(marca.strip(), '').strip()
            return descricao

        def removerTipoEmbalagemDescricao(descricao, tipoembalagem):
            descricao = descricao.replace(tipoembalagem.strip(), '').strip()
            return descricao

        def removerPalavrasSecaoDescricao(DataSet, CodigoSecao, texto_remover):
            if CodigoSecao in DataSet['CodSecao'].values:
                texto_remover_escapado = re.escape(texto_remover)
                DataSet.loc[DataSet['CodSecao'] == CodigoSecao, 'DescricaoProduto'] = DataSet.loc[DataSet['CodSecao'] == CodigoSecao, 'DescricaoProduto'].str.replace(fr'\b{texto_remover_escapado}\b', '', case=False,regex=True)
            else:
                print(f"Seção com código {CodigoSecao} não encontrada.")


        def adicionarPalavrasSecaoDescricao(Data, CodigoSecao, texto_adicionar,inicio):
            if CodigoSecao in Data['CodSecao'].values:
                if inicio:
                    mask = (Data['CodSecao'] == CodigoSecao)
                    Data.loc[mask, 'DescricaoProduto'] = Data.loc[mask, 'DescricaoProduto'].apply(
                        lambda x: x if texto_adicionar.strip().lower() in x.lower() else texto_adicionar + x
                    )
                    
                else:
                    mask = (Data['CodSecao'] == CodigoSecao)
                    Data.loc[mask, 'DescricaoProduto'] = Data.loc[mask, 'DescricaoProduto'].apply(
                        lambda x: x if texto_adicionar.strip().lower() in x.lower() else x  +  texto_adicionar
                    )
            else:
                print(f"Seção com código {CodigoSecao} não encontrada.")


        def substituirPalavrasSecaoDescricao(Data, CodigoSecao, texto_substituir,novo_texto):
            if CodigoSecao in Data['CodSecao'].values:
                Data.loc[Data['CodSecao'] == CodigoSecao, 'DescricaoProduto'] = (
                    Data.loc[Data['CodSecao'] == CodigoSecao, 'DescricaoProduto'].str.replace(texto_substituir, novo_texto, regex=False)
                )
            else:
                print(f"Seção com código {CodigoSecao} não encontrada.")
                
                
        def editarDescricaoProduto(Data, CodigoProduto,novo_texto):
            if CodigoProduto in Data['CodigoProduto'].values:
                Data.loc[Data['CodigoProduto'] == CodigoProduto, 'DescricaoProduto'] = novo_texto
            else:
                print(f"Produto com código {CodigoProduto} não encontrada.")
                
        def atribuirValorCampoLista(lista,DataSet):
            for item in lista:
                for key, value in item.items():
                    match key:
                        case 'CampoTroca':
                            campoTroca = value
                        case 'Filtro':
                            campoFiltro = value
                        case 'NovoValor':
                            campoNovoValor = value
                DataSet.loc[campoFiltro, campoTroca] = campoNovoValor
