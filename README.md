## Índices
* [Objetivo](#Objetivo)
* [Requisitos do Projeto](#Requisitos-do-Projeto)
  *  [Requisitos Funcionais](#Requisitos-Funcionais)
  *  [Requisitos Não Funcionais](#Requisitos-Não-Funcionais)

* [Tecnologias Utilizadas](#Tecnologias-Utilizadas)
  * [Banco de dados](#Iniciar-Banco-de-dados)
  * [Back-End](#Back-End)
  * [CI/CD](#CICD)
  * [Testes de Qualidade](#Testes-de-qualidade)
* [Como iniciar o projeto](#Como-iniciar)
  * [Repositório](#Repositório)
* [Alertas e recomendações](#Alertas-e-Recomendações)


# Objetivo
Este projeto tem como foco criar um algoritmo de recomendação de produtos com base na similaridade entre os produtos, utilizando variáveis como peso da embalagem, quantidade que contém em cada pacote, descrição do produto, unidade de venda, código da marca, código da seção e código do departamento. O intuito principal é descobrir quais produtos que contém em uma base de dados é mais semelhante ao produto base escolhido pelo usuário. Será utilizado KNN como algoritmo para aprendizagem e recomendação.

# Escopo
1. Manipulação de arquivos CSV
   * Upload de arquivo CSV.
   * Remoção de arquivo.
2. Tratamento de dados
   * Editar valor de campo desejado.
   * Remover valor desejado.
   * Substituir valor desejado.
   * Deletar registro de tratamento de dados de um arquivo CSV específico.
3. Treinamento
   * Buscar todos os tratamentos de dados para aplicar ao dataset alvo, gerando o modelo treinado.
4. Recomendação
   * Recomendar todos os produtos que são relacionados com outro produto que contém na base.
   * Recomendar produto em específico com base no código do produto


# Requisitos do Projeto
## Requisitos Funcionais
### 1. Manipulação de Arquivos CSV
* O sistema deve permitir o upload de arquivos no formato CSV.
* O sistema deve possibilitar a remoção de arquivos CSV.

### 2. Tratamento de Dados
* O sistema deve permitir que o usuário edite valores específicos em campos de um arquivo CSV.
* O sistema deve possibilitar a remoção de valores específicos em campos de um arquivo CSV.
* O sistema deve permitir a substituição de valores específicos em campos de um arquivo CSV.
* O sistema deve possibilitar a exclusão de registros de um arquivo CSV.

### 3. Treinamento
* O sistema deve buscar e aplicar todos os devidos tratamentos de dados na base de dados escolhida pelo usuário.
* O sistema deve realizar o treinamento de um modelo de recomendação de produtos usando a base de dados escolhida pelo usuário.

### 4. Recomendação
* O sistema deve recomendar produtos relacionados a um produto específico disponível na base de dados. 
* O sistema deve fornecer recomendações de produtos específicos com base no código do produto escolhido pelo usuário.


## Requisitos Não Funcionais
### 1. Usabilidade
* RNF1 - Interface Intuitiva (API): A API deve ter endpoints bem documentados (por exemplo, utilizando Swagger ou API Blueprint), para facilitar a compreensão e utilização por desenvolvedores.
* RNF2 - Documentação Completa: A API deve ser acompanhada por uma documentação clara e detalhada, explicando todos os endpoints, parâmetros, exemplos de uso e códigos de resposta.
### 2. Confiabilidade
* RNF3 - Tolerância a Falhas: O sistema deve ser resiliente, garantindo que falhas em um módulo não comprometam o funcionamento de outros módulos. Ele deve ser capaz de retomar o processamento após falhas e salvar o estado das operações críticas.
* RNF4 - Backup e Recuperação: O sistema deve realizar backups periódicos dos dados (datasets, modelos treinados e logs), com mecanismos de recuperação em caso de falhas ou perda de dados.
* RNF5 - Consistência dos Dados: Em caso de falhas durante operações críticas, como a aplicação de regras de tratamento ou treinamento de modelos, o sistema deve garantir que os dados permanecem consistentes, evitando estados intermediários corrompidos.



# Diagramas
## Diagrama de classe

```mermaid
classDiagram
    class Usuarios {
        +Integer USUid
        +String USUsername
        +String USUpassword
        +DateTime USUcreated_at
        +relationship Modelos[0..*]
        +relationship Arquivos[0..*]
    }
    
    class Modelos {
        +Integer MDId
        +String MDVersao
        +LargeBinary MDArquivo
        +Integer MDIdArquivoProd
        +LargeBinary MDArquivoProdAlterado
        +LargeBinary MDArquivoScaler
        +LargeBinary MDArquivoEncoder
        +LargeBinary MDArquivoPca
        +LargeBinary MDVetorTF
        +Integer MDNumeroPCA
        +Integer MDQtdeRecomendacao
        +Integer MDIdUsuario
        +Date MDDataPostagem
        +relationship Usuarios [1]
        +relationship Arquivos [0..*]
    }
    
    class Arquivos {
        +Integer APId
        +Date APDataPostagem
        +LargeBinary APArquivo
        +String APArquivoDelimiter
        +Integer APQtdeProdutos
        +Integer APIdUsuario
        +String APVersao
        +relationship Usuarios [1]
        +relationship Modelos [0..*]
    }
    Usuarios "1" --o "0..*" Modelos : contains
    Usuarios "1" --o "0..*" Arquivos : contains
    Modelos "0..*" --o "1" Arquivos : references
```


# Tecnologias Utilizadas

### Back-End
  * Python
    * Poetry
      * Flask
      * Scikit-Learn
      * Pandas
      * Numpy
      * Flasgger
      * NumPy
      * Re
      * Pandas
      * Pyodbc
      * Pyjwt
      * SqlAlchemy 
  

### CI/CD
* Jenkins
  *  Ngrok
* Docker

### Testes de qualidade
* PyUnit: É uma biblioteca para realização de testes unitários em Python baseada na arquitetura xUnit. É a forma mais difundida para realizar a prática de testes unitários pela comunidade Python.
   * Foram realizados diversos testes com foco em ter a porcentagem de cobertura de testes em 100%, desde em endpoints de usuário até testes em cada entidade afim de testar o fluxo de todo o CRUD.


# Como iniciar
### Iniciar Banco de dados
> [!WARNING]
> Este projeto utiliza SQL Server.
  1. Baixe o SQL Server neste link: https://www.microsoft.com/pt-br/sql-server/sql-server-downloads
  2. Inicie sua instância do SQL Server.
  3. Abra o arquivo conf.ini que tem de exemplo e preencha cada variável necessária na classe ConfiguracaoBancoDados.
     * As variáveis que devem ser preenchidas são:
       * DRIVER | Exemplo = ODBC Driver 17 for SQL Server
       * SERVER | Exemplo = localhost
       * DATABASE | Exemplo = RecomendacaoProdutos

## Repositório
Para clonar o repositório, você precisa ter o Git Bash, GitHub Desktop ou se preferir pode clonar o projeto via CURL/WGET.
1. Faça o clone do repositório
    * Git Bash: git clone https://github.com/AmarildoZoletJunior/ProjetoTCCPrivado.git
    * Curl: curl -L https://github.com/AmarildoZoletJunior/ProjetoTCCPrivado/archive/refs/heads/master.zip --output ProjetoTCCPrivado.zip
2. Para instalar todas as dependências do poetry, inicie um cmd apontado para a pasta principal do projeto.
    * Digite `pip install poetry`
    * Após o download, verifique se foi feito o download 100% sem erros.
    * Digite `poetry install` e verifique se foi instalado 100% sem erros.
    * Digite `poetry shell` dentro da pasta em que está localizado o arquivo poetry.lock
    * Após ele entrar no shell do poetry, digite `flask run --debug`

3. Para executar requisições em endpoints protegidos pelo JWT
    * no Endpoint `http://<ip>:<porta>/login`, utilize as seguintes credenciais:
      * Usuário: admin
      * Senha: admin
    * Após isto, em todo Endpoint que está protegido, faça autenticação utilizando a header `Authorization` e o valor inicial `Bearer SEU-TOKEN`

# Alertas e Recomendações 
> [!WARNING]
> As recomendações dependem 100% da qualidade dos dados, então esteja ciente que você deve ter um dataset que tenha pelo menos duas features, e que exista alguma similaridade entre os dados de cada feature.

> [!CAUTION]
> Para realizar novos treinamentos, somente é aceito arquivos CSV. Caso não seja importado arquivo no formato CSV, não será gerado um novo modelo treinado.

# Contribuições
> [!NOTE]
> Para contribuir com este projeto, abra um pull request para que possamos analisar suas edições e aprovar/rejeitar.

