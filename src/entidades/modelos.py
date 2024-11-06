from sqlalchemy import Column, Date, ForeignKey, Integer, LargeBinary, String
from sqlalchemy.orm import relationship

from src.data.base import Base


# Classe Modelos
class Modelos(Base):
    __tablename__ = 'Modelos'
    MDId = Column(Integer, primary_key=True, autoincrement=True)
    MDVersao = Column(String, nullable=False)
    MDArquivo = Column(LargeBinary, nullable=False)
    MDIdArquivoProd = Column(Integer, ForeignKey('ArquivosProdutos.APId'), nullable=False)
    MDArquivoProdAlterado = Column(LargeBinary, nullable=False)
    MDArquivoScaler = Column(LargeBinary, nullable=False)
    MDArquivoEncoder = Column(LargeBinary, nullable=False)
    MDArquivoPca = Column(LargeBinary, nullable=False)
    MDVetorTF = Column(LargeBinary, nullable=False)
    MDNumeroPCA = Column(Integer, nullable=False)
    MDQtdeRecomendacao = Column(Integer, nullable=False)
    MDIdUsuario = Column(Integer, ForeignKey('Usuarios.USUid'), nullable=False)
    MDDataPostagem = Column(Date)
    
    # Relacionamentos
    Usuarios = relationship('Usuarios', back_populates='Modelos')
    ArquivoProdutos = relationship('Arquivos', back_populates='Modelos')