import urllib.parse
import re
import time
import random
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from .base_scraper import BaseScraper
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

class ColetorAcademico(BaseScraper):
    """
    Coletor de perfis acadêmicos e publicações científicas.
    Suporta múltiplas fontes: Lattes (simulado), Google Scholar, ResearchGate, 
    ORCID, Academia.edu, SciELO, e Wikipedia.
    """
    
    def __init__(self, usar_proxy: bool = False, timeout: int = 30):
        super().__init__(rate_limit_range=(2.0, 4.0))
        self.timeout = timeout
        self.usar_proxy = usar_proxy
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        # Aplica os headers customizados na sessão do BaseScraper
        self.session.headers.update(self.headers)
        
        # Configuração das fontes acadêmicas
        self.fontes = {
            'wikipedia': {
                'url': 'https://pt.wikipedia.org/wiki/{nome}',
                'metodo': 'html',
                'seletor': '#mw-content-text p',
                'descricao': 'Wikipédia (versão PT)'
            },
            'wikipedia_en': {
                'url': 'https://en.wikipedia.org/wiki/{nome}',
                'metodo': 'html',
                'seletor': '#mw-content-text p',
                'descricao': 'Wikipedia (versão EN)'
            },
            'google_scholar': {
                'url': 'https://scholar.google.com.br/scholar?q={nome}',
                'metodo': 'html',
                'seletor': '.gs_ri',
                'descricao': 'Google Scholar (Busca Geral)'
            },
            'lattes': {
                'url': 'http://lattes.cnpq.br/{id}',
                'metodo': 'html',
                'seletor': '.curriculo',
                'descricao': 'Lattes CNPq (requer ID)',
                'requer_id': True
            },
            'researchgate': {
                'url': 'https://www.researchgate.net/profile/{nome}',
                'metodo': 'html',
                'seletor': '.nova-legacy-v2',
                'descricao': 'ResearchGate'
            },
            'orcid': {
                'url': 'https://orcid.org/{id}',
                'metodo': 'html',
                'seletor': '.orcid-summary',
                'descricao': 'ORCID (requer ID)',
                'requer_id': True
            },
            'academia': {
                'url': 'https://independent.academia.edu/{nome}',
                'metodo': 'html',
                'seletor': '.profile',
                'descricao': 'Academia.edu'
            },
            'scielo': {
                'url': 'https://search.scielo.org/?q={nome}&lang=pt',
                'metodo': 'html',
                'seletor': '.article-item',
                'descricao': 'SciELO (Busca)'
            },
            'publons': {
                'url': 'https://publons.com/researcher/{id}',
                'metodo': 'html',
                'seletor': '.researcher-profile',
                'descricao': 'Publons/Web of Science (requer ID)',
                'requer_id': True
            }
        }
        
        # Cache para evitar requisições repetidas
        self.cache = {}
        self.cache_ttl = 3600  # 1 hora
        
    def buscar_pessoa(self, nome: str, fonte: Optional[str] = None, 
                      id_academico: Optional[str] = None, 
                      profundidade: int = 1) -> Dict[str, any]:
        """
        Busca informações acadêmicas de uma pessoa.
        
        Args:
            nome: Nome da pessoa
            fonte: Fonte específica (None = todas)
            id_academico: ID específico (Lattes, ORCID, etc.)
            profundidade: Nível de detalhamento (1=resumo, 2=detalhado)
            
        Returns:
            Dicionário com informações extraídas.
            A chave 'texto_para_pipeline' contém o texto consolidado
            para uso no pipeline OSINT (processar_dados_texto).
        """
        resultado = {
            'nome': nome,
            'data_busca': datetime.now().isoformat(),
            'fontes_consultadas': [],
            'publicacoes': [],
            'formacao': [],
            'projetos': [],
            'resumo': '',
            'palavras_chave': [],
            'instituicoes': [],
            'metricas': {},
            'links': [],
            'conteudo_bruto': {},
            'texto_para_pipeline': ''
        }
        
        # Se não especificou fonte, busca em todas
        if fonte is None:
            fontes_para_buscar = list(self.fontes.keys())
        else:
            fontes_para_buscar = [fonte]
            
        # Busca em paralelo (se for múltiplas fontes)
        if len(fontes_para_buscar) > 1:
            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = {}
                for f in fontes_para_buscar:
                    future = executor.submit(
                        self._buscar_fonte, 
                        f, 
                        nome, 
                        id_academico,
                        profundidade
                    )
                    futures[future] = f
                    
                for future in as_completed(futures):
                    fonte_name = futures[future]
                    try:
                        dados_fonte = future.result(timeout=self.timeout)
                        if dados_fonte:
                            resultado['fontes_consultadas'].append(fonte_name)
                            resultado['conteudo_bruto'][fonte_name] = dados_fonte
                            # Mescla os dados extraídos
                            self._mesclar_dados(resultado, dados_fonte)
                    except Exception as e:
                        print(f"[-] Erro ao buscar na fonte {fonte_name}: {e}")
        else:
            # Busca sequencial para uma única fonte
            dados = self._buscar_fonte(
                fontes_para_buscar[0], 
                nome, 
                id_academico,
                profundidade
            )
            if dados:
                resultado['fontes_consultadas'] = [fontes_para_buscar[0]]
                resultado['conteudo_bruto'][fontes_para_buscar[0]] = dados
                self._mesclar_dados(resultado, dados)
                
        # Gera texto consolidado para o pipeline OSINT
        resultado['texto_para_pipeline'] = self._gerar_texto_consolidado(resultado)
        return resultado
    
    def _buscar_fonte(self, fonte: str, nome: str, 
                      id_academico: Optional[str] = None,
                      profundidade: int = 1) -> Optional[Dict]:
        """Busca em uma fonte específica"""
        
        fonte_config = self.fontes.get(fonte)
        if not fonte_config:
            return None
            
        # Verifica se precisa de ID
        if fonte_config.get('requer_id', False) and not id_academico:
            print(f"[-] Fonte {fonte} requer ID acadêmico")
            return None
            
        # Prepara a URL
        if fonte_config.get('requer_id', False):
            url = fonte_config['url'].format(id=id_academico)
        else:
            nome_url = self._sanitizar_nome(nome)
            url = fonte_config['url'].format(nome=nome_url)
            
        # Verifica cache
        cache_key = f"{fonte}:{url}"
        if cache_key in self.cache:
            cache_time, cache_data = self.cache[cache_key]
            if (datetime.now().timestamp() - cache_time) < self.cache_ttl:
                return cache_data
                
        try:
            print(f"[*] Buscando em {fonte_config['descricao']}: {url}")
            html = self._fetch_with_retry(url)
            
            if not html:
                return None
                
            # Extrai dados baseados na fonte
            dados = self._extract_by_source(html, fonte, nome, profundidade)
            
            # Cache
            self.cache[cache_key] = (datetime.now().timestamp(), dados)
            
            return dados
            
        except Exception as e:
            print(f"[-] Erro ao buscar em {fonte}: {e}")
            return None
            
    def _apply_rate_limit(self):
        """Aplica rate limiting aleatório antes de cada requisição."""
        sleep_time = random.uniform(*self.rate_limit_range)
        print(f"  Rate limit: aguardando {sleep_time:.2f}s...")
        time.sleep(sleep_time)

    def _fetch_with_retry(self, url: str, max_retries: int = 3) -> Optional[str]:
        """Faz fetch com retry e backoff exponencial, usando a sessão do BaseScraper."""
        for tentativa in range(max_retries):
            try:
                # Aplica rate limiting
                self._apply_rate_limit()
                
                # Verifica robots.txt antes de requisitar
                if not self._check_robots(url):
                    print(f"[-] Bloqueado pelo robots.txt: {url}")
                    return None
                
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                
                # Verifica se é HTML
                if 'text/html' in response.headers.get('content-type', ''):
                    return response.text
                else:
                    print(f"[-] Conteúdo não é HTML para {url}")
                    return None
                    
            except requests.exceptions.HTTPError as e:
                status = e.response.status_code if e.response else 0
                if status == 404:
                    print(f"[-] Página não encontrada: {url}")
                    return None
                elif status == 429:
                    wait_time = (2 ** tentativa) * 2
                    print(f"[!] Rate limit (429), esperando {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"[-] Erro HTTP {status}: {e}")
                    if tentativa == max_retries - 1:
                        return None
                    time.sleep(1)
                    
            except requests.exceptions.Timeout:
                print(f"[-] Timeout ao acessar {url}")
                if tentativa == max_retries - 1:
                    return None
                time.sleep(2)
                
            except Exception as e:
                print(f"[-] Erro inesperado: {e}")
                if tentativa == max_retries - 1:
                    return None
                time.sleep(1)
                
        return None
    
    def _extract_by_source(self, html: str, fonte: str, 
                          nome: str, profundidade: int) -> Dict:
        """Extrai dados específicos de cada fonte"""
        soup = BeautifulSoup(html, 'html.parser')
        dados = {
            'fonte': fonte,
            'texto_bruto': '',
            'publicacoes': [],
            'autores': [],
            'instituicao': '',
            'area': '',
            'metricas': {},
            'links_encontrados': []
        }
        
        if fonte in ['wikipedia', 'wikipedia_en']:
            dados = self._extrair_wikipedia(soup, dados, profundidade)
        elif fonte == 'google_scholar':
            dados = self._extrair_google_scholar(soup, dados, profundidade)
        elif fonte == 'researchgate':
            dados = self._extrair_researchgate(soup, dados, profundidade)
        elif fonte == 'lattes':
            dados = self._extrair_lattes(soup, dados, profundidade)
        elif fonte == 'scielo':
            dados = self._extrair_scielo(soup, dados, profundidade)
        else:
            # Extração genérica
            dados['texto_bruto'] = soup.get_text()
            
        return dados
    
    def _extrair_wikipedia(self, soup: BeautifulSoup, dados: Dict, 
                          profundidade: int) -> Dict:
        """Extrai informações da Wikipedia"""
        # Conteúdo principal
        div_conteudo = soup.find(id="mw-content-text")
        if div_conteudo:
            paragrafos = div_conteudo.find_all("p")
            dados['texto_bruto'] = "\n".join([
                p.get_text() for p in paragrafos 
                if p.get_text().strip()
            ])
            
        # Infobox (informações estruturadas)
        infobox = soup.find("table", class_="infobox")
        if infobox:
            for row in infobox.find_all("tr"):
                th = row.find("th")
                td = row.find("td")
                if th and td:
                    chave = th.get_text().strip().lower()
                    valor = td.get_text().strip()
                    
                    if any(termo in chave for termo in ['nascimento', 'nasc']):
                        dados['nascimento'] = valor
                    elif any(termo in chave for termo in ['morte', 'falec']):
                        dados['falecimento'] = valor
                    elif any(termo in chave for termo in ['nacionalidade', 'nacional']):
                        dados['nacionalidade'] = valor
                    elif any(termo in chave for termo in ['educação', 'educa', 'formação']):
                        dados['formacao'] = valor
                        
        # Categorias
        categorias = soup.find("div", id="catlinks")
        if categorias:
            dados['categorias'] = [
                cat.get_text().strip() 
                for cat in categorias.find_all("a")
                if cat.get_text().strip()
            ]
            
        # Links externos
        links = soup.find("div", id="toc")
        if links:
            dados['links_encontrados'] = [
                link.get('href') for link in links.find_all('a')
                if link.get('href') and link.get('href').startswith('http')
            ]
            
        return dados
    
    def _extrair_google_scholar(self, soup: BeautifulSoup, dados: Dict, 
                               profundidade: int) -> Dict:
        """Extrai informações do Google Scholar"""
        artigos = soup.select(".gs_ri")
        
        for artigo in artigos[:10]:  # Limita a 10 artigos
            titulo_elem = artigo.find("h3")
            if titulo_elem:
                titulo = titulo_elem.get_text().strip()
                
                # Autores e ano
                info = artigo.find("div", class_="gs_a")
                if info:
                    texto_info = info.get_text()
                    dados['publicacoes'].append({
                        'titulo': titulo,
                        'info': texto_info,
                        'fonte': 'Google Scholar'
                    })
                    
        # Métricas (se houver perfil)
        perfil = soup.select_one(".gsc_oci_value")
        if perfil:
            dados['metricas']['citacoes'] = perfil.get_text().strip()
            
        return dados
    
    def _extrair_researchgate(self, soup: BeautifulSoup, dados: Dict, 
                             profundidade: int) -> Dict:
        """Extrai informações do ResearchGate"""
        # Nome
        nome_elem = soup.select_one("h1.profile-header__name")
        if nome_elem:
            dados['nome_completo'] = nome_elem.get_text().strip()
            
        # Instituição
        inst_elem = soup.select_one(".profile-header__institution")
        if inst_elem:
            dados['instituicao'] = inst_elem.get_text().strip()
            
        # Área de pesquisa
        area_elem = soup.select_one(".profile-header__research-interests")
        if area_elem:
            dados['area'] = area_elem.get_text().strip()
            
        # Estatísticas
        stats = soup.select(".nova-stats__item")
        for stat in stats:
            valor = stat.select_one(".nova-stats__value")
            rotulo = stat.select_one(".nova-stats__label")
            if valor and rotulo:
                dados['metricas'][rotulo.get_text().strip()] = valor.get_text().strip()
                
        return dados
    
    def _extrair_lattes(self, soup: BeautifulSoup, dados: Dict, 
                       profundidade: int) -> Dict:
        """Extrai informações do Lattes (simulado)"""
        # Esta é uma simulação pois o Lattes tem estrutura complexa
        # Na prática, seria necessário extrair de forma mais robusta
        
        texto = soup.get_text()
        
        # Busca padrões comuns
        padrao_formacao = re.compile(r'(Doutor|Mestre|Especialista|Gradua[çã]o)')
        padrao_instituicao = re.compile(r'(Universidade|Faculdade|Instituto|Centro)')
        padrao_area = re.compile(r'(Área|Linha de pesquisa|Interesse)')
        
        # Extrai seções
        secoes = re.split(r'\n{2,}', texto)
        for secao in secoes:
            if padrao_formacao.search(secao):
                dados['formacao'].append(secao.strip())
            if padrao_instituicao.search(secao):
                dados['instituicoes'].append(secao.strip())
            if padrao_area.search(secao):
                dados['area'] = secao.strip()
                
        return dados
    
    def _extrair_scielo(self, soup: BeautifulSoup, dados: Dict, 
                       profundidade: int) -> Dict:
        """Extrai informações do SciELO"""
        artigos = soup.select(".article-item")
        
        for artigo in artigos[:10]:
            titulo = artigo.select_one(".title")
            autor = artigo.select_one(".authors")
            
            if titulo:
                dados['publicacoes'].append({
                    'titulo': titulo.get_text().strip(),
                    'autores': autor.get_text().strip() if autor else '',
                    'fonte': 'SciELO'
                })
                
        return dados
    
    def _mesclar_dados(self, resultado: Dict, dados_fonte: Dict):
        """Mescla dados de diferentes fontes"""
        # Publicações
        if 'publicacoes' in dados_fonte:
            for pub in dados_fonte['publicacoes']:
                if pub not in resultado['publicacoes']:
                    resultado['publicacoes'].append(pub)
                    
        # Instituições
        if 'instituicao' in dados_fonte and dados_fonte['instituicao']:
            if dados_fonte['instituicao'] not in resultado['instituicoes']:
                resultado['instituicoes'].append(dados_fonte['instituicao'])
                
        # Área
        if 'area' in dados_fonte and dados_fonte['area']:
            if not resultado['palavras_chave']:
                resultado['palavras_chave'] = dados_fonte['area'].split(',')
                
        # Métricas
        if 'metricas' in dados_fonte:
            resultado['metricas'].update(dados_fonte['metricas'])
            
        # Links
        if 'links_encontrados' in dados_fonte:
            resultado['links'].extend(dados_fonte['links_encontrados'])

    def _gerar_texto_consolidado(self, resultado: Dict) -> str:
        """
        Consolida todos os dados extraídos em um único texto corrido,
        compatível com o processar_dados_texto do pipeline.
        """
        partes = []
        nome = resultado.get('nome', '')

        # Cabeçalho
        partes.append(f"Perfil acadêmico de {nome}.")

        # Texto bruto das fontes
        for fonte, dados in resultado.get('conteudo_bruto', {}).items():
            texto = dados.get('texto_bruto', '').strip()
            if texto:
                partes.append(f"\n--- {fonte} ---\n{texto}")

        # Publicações
        if resultado.get('publicacoes'):
            partes.append("\nPublicações:")
            for pub in resultado['publicacoes']:
                titulo = pub.get('titulo', '')
                info = pub.get('info', '')
                partes.append(f"  - {titulo} {info}".strip())

        # Instituições
        if resultado.get('instituicoes'):
            partes.append(f"\nInstituições: {', '.join(resultado['instituicoes'])}")

        # Palavras-chave
        if resultado.get('palavras_chave'):
            partes.append(f"Áreas: {', '.join(resultado['palavras_chave'])}")

        return "\n".join(partes)
            
    def _sanitizar_nome(self, nome: str) -> str:
        """Sanitiza nome para URL"""
        # Remove acentos
        import unicodedata
        nome = unicodedata.normalize('NFKD', nome)
        nome = nome.encode('ASCII', 'ignore').decode('ASCII')
        
        # Substitui espaços
        nome = nome.replace(' ', '_')
        
        # Remove caracteres especiais
        nome = re.sub(r'[^a-zA-Z0-9_]', '', nome)
        
        return nome
    
    def buscar_por_id_lattes(self, id_lattes: str) -> Dict:
        """Busca usando ID Lattes"""
        return self.buscar_pessoa(
            nome="", 
            fonte="lattes", 
            id_academico=id_lattes
        )
    
    def buscar_por_orcid(self, orcid_id: str) -> Dict:
        """Busca usando ORCID"""
        return self.buscar_pessoa(
            nome="", 
            fonte="orcid", 
            id_academico=orcid_id
        )
    
    def buscar_multiplos_nomes(self, nomes: List[str], 
                              fontes: Optional[List[str]] = None) -> Dict[str, Dict]:
        """Busca múltiplos nomes simultaneamente"""
        resultados = {}
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {
                executor.submit(self.buscar_pessoa, nome, fontes): nome 
                for nome in nomes
            }
            
            for future in as_completed(futures):
                nome = futures[future]
                try:
                    resultados[nome] = future.result(timeout=self.timeout)
                except Exception as e:
                    print(f"[-] Erro ao buscar {nome}: {e}")
                    resultados[nome] = {'erro': str(e)}
                    
        return resultados
    
    def extrair_citacoes(self, texto: str) -> List[str]:
        """Extrai citações acadêmicas de um texto"""
        padrao = re.compile(
            r'\([A-Z][a-z]+ et al\., \d{4}\)|'
            r'[A-Z][a-z]+ et al\. \(\d{4}\)|'
            r'\([A-Z][a-z]+, \d{4}\)'
        )
        return padrao.findall(texto)
    
    def limpar_cache(self):
        """Limpa o cache de dados"""
        self.cache.clear()
        print("[+] Cache limpo")
        
    def estatisticas_cache(self) -> Dict:
        """Retorna estatísticas do cache"""
        return {
            'tamanho': len(self.cache),
            'ttl': self.cache_ttl,
            'chaves': list(self.cache.keys())[:10]
        }