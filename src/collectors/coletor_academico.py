import urllib.parse
from .base_scraper import BaseScraper
import requests

class ColetorAcademico(BaseScraper):
    """
    Simula um coletor de perfis públicos acadêmicos.
    Para esta PoC didática, iremos extrair páginas da Wikipedia de figuras públicas conhecidas 
    ao invés do Lattes diretamente, para evitar CAPTCHAs e violações de Termos de Serviço, 
    demonstrando o funcionamento do pipeline de NLP e Banco de Dados.
    """
    def __init__(self):
        super().__init__(rate_limit_range=(2.0, 4.0))
        self.base_url = "https://pt.wikipedia.org/wiki/"

    def buscar_pessoa(self, nome):
        """Busca por uma pessoa e retorna o conteúdo em texto da página."""
        # Limpar o nome para a URL
        nome_limpo = urllib.parse.quote(nome.replace(" ", "_"))
        url = f"{self.base_url}{nome_limpo}"
        
        try:
            print(f"[*] Buscando dados acadêmicos para {nome} em {url}...")
            html = self.fetch(url)
            soup = self.parse_html(html)
            
            # Extrair parágrafos do conteúdo principal
            div_conteudo = soup.find(id="mw-content-text")
            if not div_conteudo:
                return ""
                
            paragrafos = div_conteudo.find_all("p")
            conteudo_texto = "\n".join([p.get_text() for p in paragrafos if p.get_text().strip()])
            
            print(f"[+] Foram extraídos {len(conteudo_texto)} caracteres de texto.")
            return conteudo_texto
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                print(f"[-] Perfil não encontrado para: {nome}")
            else:
                print(f"[-] Erro HTTP: {e}")
            return ""
        except PermissionError as e:
            print(f"[-] {e}")
            return ""
        except Exception as e:
            print(f"[-] Erro inesperado ao buscar {nome}: {e}")
            return ""
