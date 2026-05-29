import os
import requests
from .base_scraper import BaseScraper

class ColetorTransparenciaCGU(BaseScraper):
    """
    Coletor para a API de Dados Abertos do Portal da Transparência (CGU).
    Requer uma chave de API gratuita obtida no site do Portal.
    """
    def __init__(self):
        super().__init__(rate_limit_range=(1.0, 2.0))
        self.base_url = "https://api.portaldatransparencia.gov.br/api-de-dados"
        self.chave_api = os.getenv("CGU_API_KEY")
        
        if self.chave_api:
            self.session.headers.update({"chave-api-dados": self.chave_api})

    def buscar_sancoes_por_cnpj(self, cnpj):
        """Busca sanções aplicadas a uma empresa (CEIS/CNEP/CEPIM)"""
        if not self.chave_api:
            print("[-] Chave da API da CGU (CGU_API_KEY) não configurada. Pulando busca de sanções.")
            return None
            
        cnpj_limpo = "".join(filter(str.isdigit, cnpj))
        # Endpoints de sanções: /sancoes
        url = f"{self.base_url}/sancoes?cnpjSancionado={cnpj_limpo}&pagina=1"
        
        try:
            print(f"[*] CGU: Buscando sanções para o CNPJ {cnpj_limpo}...")
            response = self.session.get(url)
            
            if response.status_code == 401:
                print("[-] CGU: Chave de API inválida ou não autorizada.")
                return None
                
            response.raise_for_status()
            dados = response.json()
            
            if dados:
                print(f"[!] CGU: Foram encontradas {len(dados)} sanções para este CNPJ.")
            else:
                print("[+] CGU: Nenhuma sanção encontrada (Ficha Limpa).")
                
            return dados
            
        except requests.exceptions.RequestException as e:
            print(f"[-] Erro ao consultar API da CGU: {e}")
            return None
