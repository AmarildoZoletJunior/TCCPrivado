from sqlalchemy import (Column, Date, ForeignKey, Integer, LargeBinary, String,
                        func)
from sqlalchemy.orm import relationship

from src.data.base import Base


# Classe Arquivos
class Arquivos(Base):
    __tablename__ = 'ArquivosProdutos'
    APId = Column(Integer, primary_key=True, autoincrement=True)
    APDataPostagem = Column(Date, default=func.now())
    APArquivo = Column(LargeBinary, nullable=False)
    APArquivoDelimiter = Column(String, nullable=False)
    APQtdeProdutos = Column(Integer, nullable=False)
    APIdUsuario = Column(Integer, ForeignKey('Usuarios.USUid'), nullable=False)
    APVersao = Column(String, nullable=False)
    
    # Relacionamentos
    Usuarios = relationship('Usuarios', back_populates='Arquivos')
    Modelos = relationship('Modelos', back_populates='ArquivoProdutos')