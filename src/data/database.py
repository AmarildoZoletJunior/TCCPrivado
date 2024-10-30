
from src.dtos.arquivosDTO import ArquivoProdutosDTO
from src.dtos.modelosDTO import ModelosDTO
from src.dtos.usuariosDTO import UsuariosDTO
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker

from src.config import configuration
import urllib

from src.entidades.usuarios import Usuarios
from src.entidades.modelos import Modelos
from src.entidades.arquivos import Arquivos


from src.data.base import Base

class Database:
    def __init__(self):
        self.engine = self.ConnectDataBase()
        if isinstance(self.engine, str):
            print(self.engine)
        else:
            self.Session = sessionmaker(bind=self.engine)
            self.VerifyBaseTables()

    def VerifyBaseTables(self):
        try:
            Base.metadata.create_all(self.engine, checkfirst=True)
        except Exception as e:
            print(f"Ocorreu um erro ao criar as tabelas do banco, verifique a conexão")
            print(str(e))

    def ConnectDataBase(self):
        try:
            params = urllib.parse.quote_plus(
                f"DRIVER={configuration.DRIVER};"
                f"SERVER={configuration.SERVER};"
                f"DATABASE={configuration.DATABASE};"
                f"Trusted_Connection=yes;"
            )
            engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}", echo=True)
            with engine.connect() as connection:
                pass
            return engine
        except Exception as e:
            error_message = f'Ocorreu um erro ao conectar-se ao banco de dados: {str(e)}'
            return error_message
        
        

    def DoSelectWithRelations(self, model, relacoes=None, filtros=None):
        if isinstance(self.engine, str):
            return []

        with self.Session() as session:
            query = session.query(model)
            if filtros:
                query = query.filter_by(**filtros)
            if relacoes:
                for relacao in relacoes:
                    query = query.join(relacao)
            results = query.all()
            dto_list = [self.convert_to_dto(result) for result in results]

            return dto_list


    def DoSelect(self, model, **filters):
        if isinstance(self.engine, str):
            return []
        try:
            with self.Session() as session:
                query = session.query(model).filter_by(**filters)
                results = query.all()
                dto_list = [self.convert_to_dto(result) for result in results]
                return dto_list
        except Exception as e:
            print(f"Erro ao realizar DoSelect: {e}")
            return []

    def objectToDict(self, obj):
        if obj is None:
            return None
        return {column.name: getattr(obj, column.name) for column in obj.__table__.columns}

    def DoInsert(self, model, **data):
        if isinstance(self.engine, str):
            return None
        with self.Session() as session:
            try:
                new_record = model(**data)
                session.add(new_record)
                session.commit()
                return self.objectToDict(new_record)
            except Exception as e:
                session.rollback()
                print(f"Erro ao inserir dados: {e}")
                return None
            
    def DoUpdate(self, model, filters: dict, update_data: dict):
        if isinstance(self.engine, str):
            return None
        
        with self.Session() as session:
            try:
                query = session.query(model).filter_by(**filters)
                updated_count = query.update(update_data, synchronize_session=False)
                session.commit()
                return updated_count
            except Exception as e:
                session.rollback()
                print(f"Erro ao atualizar dados: {e}")
                return None
            
            
    def DoDelete(self, model, **filters):
        if isinstance(self.engine, str):
            return None
        with self.Session() as session:
            try:
                query = session.query(model).filter_by(**filters)
                deleted_count = query.delete(synchronize_session=False)
                session.commit()
                return deleted_count
            except Exception as e:
                session.rollback()
                print(f"Erro ao deletar dados: {e}")
                return None

    
    def convert_to_dto(self, model_instance):
        if isinstance(model_instance, Arquivos):
            return ArquivoProdutosDTO(
                id=model_instance.APId,
                data_postagem=model_instance.APDataPostagem,
                arquivo=model_instance.APArquivo,
                delimiter=model_instance.APArquivoDelimiter,
                qtde_produtos=model_instance.APQtdeProdutos,
                id_usuario=model_instance.APIdUsuario,
                versao=model_instance.APVersao
            ).to_dict()

        elif isinstance(model_instance, Modelos):
            return ModelosDTO(
                id=model_instance.MDId,
                versao=model_instance.MDVersao,
                arquivo=model_instance.MDArquivo,
                id_arquivo_prod=model_instance.MDIdArquivoProd,
                arquivo_produto_alterado = model_instance.MDArquivoProdAlterado,
                scaler=model_instance.MDArquivoScaler,
                encoder=model_instance.MDArquivoEncoder,
                pca=model_instance.MDArquivoPca,
                vetor_tf=model_instance.MDVetorTF,
                num_pca=model_instance.MDNumeroPCA,
                qtde_recomendacao=model_instance.MDQtdeRecomendacao,
                id_usuario=model_instance.MDIdUsuario,
                data_postagem=model_instance.MDDataPostagem
            ).to_dict()

        elif isinstance(model_instance, Usuarios):
            return UsuariosDTO(
                id=model_instance.USUid,
                username=model_instance.USUsername,
                password=model_instance.USUpassword,
                created_at=model_instance.USUcreated_at
            ).to_dict()

        return None