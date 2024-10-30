from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from src.data.base import Base
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.sql import func

class Usuarios(Base):
    __tablename__ = 'Usuarios'
    USUid = Column(Integer, primary_key=True, autoincrement=True)
    USUsername = Column(String, nullable=False)
    USUpassword = Column(String, nullable=False)
    USUcreated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    Modelos = relationship('Modelos', back_populates='Usuarios')
    Arquivos = relationship('Arquivos', back_populates='Usuarios')