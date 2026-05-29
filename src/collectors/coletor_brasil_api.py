import requests
from .base_scraper import BaseScraper

class ColetorBrasilAPI(BaseScraper):
    """
    Coletor para a Brasil API, para enriquecimento de dados de OSINT
    buscando informações de CNPJ, CEP e DDD.
    """
    def __init__(self):
        super().__init__(rate_limit_range=(0.5, 1.5))
        self.base_url = "https://brasilapi.com.br/api"

    def buscar_cnpj(self, cnpj):
        cnpj_limpo = "".join(filter(str.isdigit, cnpj))
        if len(cnpj_limpo) != 14: return None
        url = f"{self.base_url}/cnpj/v1/{cnpj_limpo}"
        try:
            print(f"[*] Brasil API: Buscando CNPJ {cnpj_limpo}...")
            response = self.session.get(url)
            if response.status_code == 404: return None
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return None

    def buscar_ddd(self, ddd):
        ddd_limpo = "".join(filter(str.isdigit, str(ddd)))
        if len(ddd_limpo) != 2: return None
        url = f"{self.base_url}/ddd/v1/{ddd_limpo}"
        try:
            print(f"[*] Brasil API: Buscando DDD {ddd_limpo}...")
            response = self.session.get(url)
            if response.status_code == 404: return None
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return None

    def buscar_cep(self, cep):
        cep_limpo = "".join(filter(str.isdigit, cep))
        if len(cep_limpo) != 8: return None
        url = f"{self.base_url}/cep/v2/{cep_limpo}"
        try:
            print(f"[*] Brasil API: Buscando CEP {cep_limpo}...")
            response = self.session.get(url)
            if response.status_code == 404: return None
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return None
