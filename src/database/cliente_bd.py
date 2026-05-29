import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .modelos import Base

class ClienteBD:
    def __init__(self, db_url=None):
        if not db_url:
            # Padrão para o postgres do docker-compose se não for fornecido
            # Formato: postgresql://usuario:senha@host:porta/nomedobanco
            db_url = os.getenv("DATABASE_URL", "sqlite:///osint_db.sqlite3")
            
        self.engine = create_engine(db_url, echo=False)
        self.Session = sessionmaker(bind=self.engine)
        
    def iniciar_bd(self):
        """Cria as tabelas se elas não existirem."""
        Base.metadata.create_all(self.engine)
        print("[*] Tabelas do banco de dados inicializadas.")

    def obter_sessao(self):
        return self.Session()
