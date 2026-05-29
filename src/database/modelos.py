from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, JSON
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class Pessoa(Base):
    __tablename__ = 'pessoas'
    
    id = Column(Integer, primary_key=True)
    nome = Column(String(255), nullable=False)
    # Armazenando dados JSON estruturados em vez de colunas rígidas
    metadados_json = Column(JSON, default=dict) 
    criado_em = Column(DateTime, default=datetime.utcnow)
    
    dados_brutos = relationship("DadosBrutos", back_populates="pessoa", cascade="all, delete-orphan")
    relacoes = relationship("RelacaoEntidade", back_populates="pessoa", cascade="all, delete-orphan")

class RelacaoEntidade(Base):
    __tablename__ = 'relacoes_entidade'
    
    id = Column(Integer, primary_key=True)
    pessoa_id = Column(Integer, ForeignKey('pessoas.id'), nullable=False)
    
    tipo_entidade = Column(String(50), nullable=False) # ex., 'ORG', 'LOC'
    nome_entidade = Column(String(255), nullable=False) # ex., 'Universidade de São Paulo'
    
    pessoa = relationship("Pessoa", back_populates="relacoes")

class DadosBrutos(Base):
    """Armazena o texto bruto raspado (e anonimizado) para auditoria ou reprocessamento."""
    __tablename__ = 'dados_brutos'
    
    id = Column(Integer, primary_key=True)
    pessoa_id = Column(Integer, ForeignKey('pessoas.id'), nullable=False)
    url_origem = Column(String(500))
    conteudo_anonimizado = Column(Text)
    raspado_em = Column(DateTime, default=datetime.utcnow)
    
    pessoa = relationship("Pessoa", back_populates="dados_brutos")
