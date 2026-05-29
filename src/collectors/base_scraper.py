import time
import random
import requests
import urllib.robotparser
from urllib.parse import urlparse
from bs4 import BeautifulSoup

class BaseScraper:
    def __init__(self, user_agent=None, rate_limit_range=(1.0, 3.0)):
        self.user_agent = user_agent or "OSINT-Bot/1.0 (PoC Educacional; +http://example.com/bot)"
        self.rate_limit_range = rate_limit_range
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.user_agent})
        self.rp = urllib.robotparser.RobotFileParser()
        self.robots_cache = {}

    def _check_robots(self, url):
        parsed_url = urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        
        if base_url not in self.robots_cache:
            robots_url = f"{base_url}/robots.txt"
            self.rp.set_url(robots_url)
            try:
                self.rp.read()
                self.robots_cache[base_url] = True
            except Exception as e:
                print(f"Aviso: Não foi possível ler o robots.txt de {base_url}: {e}")
                self.robots_cache[base_url] = False
                
        # Se conseguimos ler o robots.txt, verifica se é permitido
        if self.robots_cache[base_url]:
            return self.rp.can_fetch(self.user_agent, url)
        return True # Padrão True caso não exista robots.txt

    def fetch(self, url):
        """Busca uma URL, respeitando o robots.txt e aplicando rate limiting."""
        if not self._check_robots(url):
            raise PermissionError(f"Scraping não permitido pelo robots.txt para a URL: {url}")
            
        # Lógica de limite de requisições (Rate limiting)
        sleep_time = random.uniform(*self.rate_limit_range)
        print(f"Rate limit: Aguardando {sleep_time:.2f} segundos antes de buscar...")
        time.sleep(sleep_time)
        
        response = self.session.get(url)
        response.raise_for_status()
        return response.text

    def parse_html(self, html_content):
        return BeautifulSoup(html_content, "html.parser")
