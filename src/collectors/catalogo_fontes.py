import urllib.parse

class CatalogoFontesOSINT:
    """
    Mantém o mapeamento de centenas de fontes OSINT do Brasil.
    Gera URLs dinâmicas pré-preenchidas para facilitar a busca manual.
    """
    def __init__(self):
        self.fontes = {
            "CNPJ": {
                "Receita Federal (Comprovante)": "https://solucoes.receita.fazenda.gov.br/servicos/cnpjreva/cnpjreva_solicitacao.asp",
                "Portal da Transparência (Sanções/CEIS)": "http://www.portaltransparencia.gov.br/sancoes/ceis?tabelaGerada=true&textoPesquisa={dado}",
                "JusBrasil (Processos Judiciais)": "https://www.jusbrasil.com.br/consulta-processual/busca?q={dado}",
                "RedeCNPJ (Societário Visual)": "https://www.redecnpj.com.br/rede/",
                "CNPJ.info (Dados Básicos)": "https://cnpj.info/{dado}",
                "CNPJ.ws (API Pública)": "https://cnpj.ws/{dado}/",
                "Empresas.cn (Dados Completos)": "https://empresas.cn/cnpj/{dado}",
                "Consulta CNPJ (Brasil.io)": "https://brasil.io/cnpj/{dado}",
                "Serpro (Consulta Gratuita)": "https://www.serpro.gov.br/consulta-cnpj/",
                "Receita Federal (Cartão CNPJ)": "https://servicos.receita.fazenda.gov.br/servicos/cnpjreva/consultar.asp",
                "SIARE (Recuperação Judicial)": "https://www.siare.trf5.jus.br/",
                "Tabelionato de Protesto": "https://www.tabeliaodeprotesto.org.br/",
                "CNDT (Certidão Débitos Trabalhistas)": "https://consulta-cndt.sit.trabalho.gov.br/consulta/",
                "FGTS (Certidão)": "https://www.caixa.gov.br/site/Paginas/certidao-conjunta-fgts.aspx",
                "INSS (Certidão Débitos)": "https://certidaonegativa.inss.gov.br/",
            },
            "CPF": {
                "Situação Cadastral Receita Federal": "https://servicos.receita.fazenda.gov.br/Servicos/CPF/ConsultaSituacao/ConsultaPublica.asp",
                "Portal da Transparência (Servidores/Benefícios)": "https://portaldatransparencia.gov.br/busca?termo={dado}",
                "Escavador (Processos e Currículo)": "https://www.escavador.com/busca?q={dado}",
                "TSE - Certidão de Quitação": "https://www.tse.jus.br/servicos-eleitorais/autoatendimento-eleitoral#/certidoes-eleitor/certidao-quitacao-eleitoral",
                "Valores a Receber (Banco Central)": "https://valoresareceber.bcb.gov.br/publico/",
                "SERASA (Consulta Gratuita)": "https://www.serasa.com.br/consulta-cpf/",
                "Boletim de Ocorrência Online": "https://www.delegaciaeletronica.policiacivil.sp.gov.br/ssp-delegacia-eletronica/",
                "Registro de Ocorrência (MG)": "https://www.delegaciaeletronica.mg.gov.br/",
                "Divulgador de CPF (Lei Geral)": "https://www.detran.sp.gov.br/",
                "CadÚnico (Consulta Cidadão)": "https://cadunico.dataprev.gov.br/",
                "Meu INSS (Extrato)": "https://meu.inss.gov.br/",
                "Caged (Vínculos Trabalhistas)": "https://app.powerbi.com/view?r=eyJrIjoiYzA2NzU5MjAtYzA1Yi00",
                "Consulta PIS/PASEP": "https://www.caixa.gov.br/beneficios-trabalhador/pis-pasep/Paginas/default.aspx",
                "SPC Brasil": "https://www.spcbrasil.org.br/",
            },
            "USUARIO": {
                # Redes Sociais (expansão)
                "Instagram": "https://www.instagram.com/{dado}/",
                "Twitter / X": "https://x.com/{dado}",
                "Facebook": "https://www.facebook.com/{dado}",
                "TikTok": "https://www.tiktok.com/@{dado}",
                "LinkedIn": "https://www.linkedin.com/in/{dado}/",
                "Pinterest": "https://www.pinterest.com/{dado}/",
                "Reddit": "https://www.reddit.com/user/{dado}",
                "Tumblr": "https://{dado}.tumblr.com",
                "Snapchat": "https://www.snapchat.com/add/{dado}",
                "Threads": "https://www.threads.net/@{dado}",
                "Bluesky": "https://bsky.app/profile/{dado}",
                "Mastodon": "https://mastodon.social/@{dado}",
                "Discord": "https://discord.com/users/{dado}",
                "Telegram": "https://t.me/{dado}",
                "WhatsApp (Clique para conversar)": "https://wa.me/{dado}",
                "Signal": "https://signal.me/#p/{dado}",
                "VK": "https://vk.com/{dado}",
                "Weibo": "https://weibo.com/u/{dado}",
                "Bilibili": "https://space.bilibili.com/{dado}",
                
                # Desenvolvimento
                "GitHub": "https://github.com/{dado}",
                "GitLab": "https://gitlab.com/{dado}",
                "Bitbucket": "https://bitbucket.org/{dado}/",
                "SourceForge": "https://sourceforge.net/u/{dado}/",
                "Codeberg": "https://codeberg.org/{dado}",
                "Stack Overflow": "https://stackoverflow.com/users/?tab=accounts&SearchText={dado}",
                "Dev.to": "https://dev.to/{dado}",
                "Medium": "https://medium.com/@{dado}",
                "Hashnode": "https://hashnode.com/@{dado}",
                "Substack": "https://{dado}.substack.com",
                "HackerNews": "https://news.ycombinator.com/user?id={dado}",
                "LeetCode": "https://leetcode.com/{dado}/",
                "Codeforces": "https://codeforces.com/profile/{dado}",
                "Kaggle": "https://www.kaggle.com/{dado}",
                "Replit": "https://replit.com/@{dado}",
                "CodePen": "https://codepen.io/{dado}",
                "Docker Hub": "https://hub.docker.com/u/{dado}",
                
                # Conteúdo
                "YouTube": "https://www.youtube.com/@{dado}",
                "Twitch": "https://www.twitch.tv/{dado}",
                "Spotify": "https://open.spotify.com/user/{dado}",
                "SoundCloud": "https://soundcloud.com/{dado}",
                "Bandcamp": "https://bandcamp.com/{dado}",
                "Vimeo": "https://vimeo.com/{dado}",
                "Dailymotion": "https://www.dailymotion.com/{dado}",
                "Rumble": "https://rumble.com/user/{dado}",
                "Kick": "https://kick.com/{dado}",
                
                # Gaming
                "Steam": "https://steamcommunity.com/id/{dado}",
                "Epic Games": "https://www.epicgames.com/id/{dado}",
                "Xbox": "https://www.xbox.com/en-US/play/user/{dado}",
                "PlayStation": "https://psnprofiles.com/{dado}",
                "Battle.net": "https://www.battle.net/{dado}",
                
                # Outros
                "Keybase": "https://keybase.io/{dado}",
                "Gravatar": "https://en.gravatar.com/{dado}",
                "Patreon": "https://www.patreon.com/{dado}",
                "Linktree": "https://linktr.ee/{dado}",
                "Beacons": "https://beacons.ai/{dado}",
                "About.me": "https://about.me/{dado}",
                "Product Hunt": "https://www.producthunt.com/@{dado}",
                "Quora": "https://www.quora.com/profile/{dado}",
                
                # Google Dorks para Usuário
                "Google Dork (Perfis)": "https://www.google.com/search?q=%22{dado_url}%22+site%3Ainstagram.com+OR+site%3Atwitter.com+OR+site%3Afacebook.com+OR+site%3Alinkedin.com",
                "Google Dork (Menções)": "https://www.google.com/search?q=%22{dado_url}%22+-site%3A{dado_url}",
                "Google Imagens": "https://www.google.com/search?q=%22{dado_url}%22&tbm=isch",
                "Bing (Perfis)": "https://www.bing.com/search?q=%22{dado_url}%22+instagram+OR+twitter+OR+facebook",
                "Yandex (Imagens)": "https://yandex.com/images/search?text={dado_url}",
            },
            "NOME": {
                # Justiça e Processos
                "JusBrasil (Processos)": "https://www.jusbrasil.com.br/consulta-processual/busca?q={dado_url}",
                "Escavador": "https://www.escavador.com/busca?q={dado_url}",
                "CNJ (Consulta Processual)": "https://consultaprocessual.cnj.jus.br/consultaprocessual/",
                "TRF1 (Justiça Federal 1)": "https://processual.trf1.jus.br/consultaProcessual/",
                "TRF2 (Justiça Federal 2)": "https://www10.trf2.jus.br/consulta-processual/",
                "TRF3 (Justiça Federal 3)": "https://pje.trf3.jus.br/consulta/",
                "TRF4 (Justiça Federal 4)": "https://eproc.trf4.jus.br/eproc/controlador.php?acao=acessar_sistema",
                "TRF5 (Justiça Federal 5)": "https://pje.trf5.jus.br/pje/ConsultaPublica/",
                "TJSP (Consulta Processual)": "https://esaj.tjsp.jus.br/esaj/",
                "TJRJ": "https://www4.tjrj.jus.br/consulta-processual/",
                "TJMG": "https://www8.tjmg.jus.br/pjecoram/controlador.php?acao=processo_consulta_publica",
                "TJRS": "https://www.tjrs.jus.br/busca/?tb=processos",
                "TJPR": "https://projudi.tjpr.jus.br/consulta/",
                "TJBA": "https://pje.tjba.jus.br/pje/ConsultaPublica/",
                "TJPE": "https://www.tjpe.jus.br/consulta-processual",
                
                # Transparência Pública
                "Portal da Transparência (Viagens/Salários)": "https://portaldatransparencia.gov.br/busca?termo={dado_url}",
                "Portal de Precatórios (TRF5)": "https://rpvprecatorio.trf5.jus.br/",
                "Diário Oficial da União": "https://pesquisa.in.gov.br/imprensa/jsp/visualiza/index.jsp?data=01/01/2024&jornal=1&pagina=1&totalArquivos=1",
                "Diários Oficiais Estaduais (Busca)": "https://www.diariooficial.com.br/busca",
                
                # Acadêmico
                "Lattes (CNPq)": "https://buscatextual.cnpq.br/buscatextual/busca.do",
                "Google Acadêmico": "https://scholar.google.com.br/scholar?q={dado_url}",
                "ResearchGate": "https://www.researchgate.net/search/publication?q={dado_url}",
                "Academia.edu": "https://www.academia.edu/search?q={dado_url}",
                "SciELO": "https://search.scielo.org/?q={dado_url}",
                
                # Profissional
                "LinkedIn": "https://www.linkedin.com/search/results/all/?keywords={dado_url}",
                "InfoJobs (Currículos)": "https://www.infojobs.com.br/busca-curriculo.aspx?q={dado_url}",
                "Catho (Currículos)": "https://www.catho.com.br/curriculos/busca?q={dado_url}",
                "Vagas.com (Currículos)": "https://www.vagas.com.br/curriculos/resultado?q={dado_url}",
                "Indeed (Currículos)": "https://br.indeed.com/jobs?q={dado_url}",
                
                # Eleitoral
                "TSE (Filiados)": "https://divulgacandcontas.tse.jus.br/divulga/#/",
                "TSE (Candidaturas)": "https://www.tse.jus.br/eleicoes/eleicoes-anteriores",
                "TRE (Consulta por Nome)": "https://www.tre-mg.jus.br/eleicoes/consulta-a-filiados",
                
                # Empresarial
                "Empresômetro (Sócios)": "https://empresometro.com.br/busca-por-socio/?nome={dado_url}",
                "QSA (Quadro Societário)": "https://qsa.app/",
                
                # Mídia Social (Busca por nome)
                "Facebook Search": "https://www.facebook.com/search/people/?q={dado_url}",
                "Instagram Search": "https://www.instagram.com/web/search/top/?q={dado_url}",
                "Twitter Search": "https://x.com/search?q={dado_url}",
                "TikTok Search": "https://www.tiktok.com/search/user?q={dado_url}",
                
                # Google Dorks para Nome
                "Google Dork (Arquivos PDF)": "https://www.google.com/search?q=%22{dado_url}%22+ext%3Apdf",
                "Google Dork (Arquivos DOC)": "https://www.google.com/search?q=%22{dado_url}%22+ext%3Adoc+OR+ext%3Adocx",
                "Google Dork (Planilhas)": "https://www.google.com/search?q=%22{dado_url}%22+ext%3Axls+OR+ext%3Axlsx",
                "Google Dork (Slides)": "https://www.google.com/search?q=%22{dado_url}%22+ext%3Appt+OR+ext%3Apptx",
                "Google Dork (CVs)": "https://www.google.com/search?q=%22{dado_url}%22+%22curriculum%22+OR+%22curr%C3%ADculo%22+OR+%22cv%22",
                "Google Dork (Processos Seletivos)": "https://www.google.com/search?q=%22{dado_url}%22+%22edital%22+OR+%22concurso%22+OR+%22sele%C3%A7%C3%A3o%22",
                "Google News": "https://news.google.com/search?q={dado_url}&hl=pt-BR",
                
                # Ferramentas Adicionais
                "Wayback Machine (Arquivo)": "https://web.archive.org/web/*/https://www.google.com/search?q={dado_url}",
                "Pimeyes (Busca Facial)": "https://pimeyes.com/en",
                "FaceCheck (Busca Facial)": "https://facecheck.id/",
                "BeenVerified": "https://www.beenverified.com/",
                "Pipl (People Search)": "https://pipl.com/search/?q={dado_url}",
            },
            "TELEFONE": {
                "Consulta Telefone (Brasil)": "https://www.consultatelefone.com.br/consulta/{dado}",
                "Quem Ligou": "https://www.quemligou.com.br/buscar/{dado}",
                "Telefone 123": "https://www.telefone123.com.br/busca/{dado}",
                "Reverse Phone Lookup (Internacional)": "https://www.reversephonelookup.com/",
                "Numlookup (Gratuito)": "https://www.numlookup.com/{dado}",
                "Truecaller (Web)": "https://www.truecaller.com/search/{dado}",
                "Sync.me": "https://sync.me/search/{dado}",
                "WhatsApp (Link Direto)": "https://wa.me/{dado}",
                "Telegram (Link Direto)": "https://t.me/{dado}",
                "Signal (Link Direto)": "https://signal.me/#p/{dado}",
                "Zaproulette (WhatsApp Aleatório)": "https://zaproulette.com/",
                "ScamNumbers.info": "https://scamnumbers.info/search/{dado}",
                "PhoneInfoga (Scanner)": "https://phoneinfoga.net/",
                "Google Dork (Telefone)": "https://www.google.com/search?q=%22{dado}%22+OR+%22{dado.replace('-','')}%22+OR+%22{dado.replace(' ','')}%22",
            },
            "EMAIL": {
                "Hunter (Verificação)": "https://hunter.io/email-verifier/{dado}",
                "Email Checker (Verificação)": "https://email-checker.net/check/{dado}",
                "Have I Been Pwned (Vazamentos)": "https://haveibeenpwned.com/account/{dado}",
                "Dehashed (Vazamentos - Pago)": "https://dehashed.com/search?query=email%3A{dado}",
                "IntelX (Breach Data)": "https://intelx.io/?s={dado}",
                "LeakCheck (Vazamentos)": "https://leakcheck.net/search?query={dado}",
                "Emailrep.io (Reputação)": "https://emailrep.io/{dado}",
                "Gravatar (Avatar)": "https://en.gravatar.com/{dado.replace('@', '')}",
                "Google Dork (Email)": "https://www.google.com/search?q=%22{dado}%22+ext%3Atxt+OR+ext%3Acsv+OR+ext%3Ajason+OR+ext%3Asql",
                "Pipl (Email Search)": "https://pipl.com/search/?q={dado}",
                "Skype (Resolve Email)": "https://www.skype.com/pt-br/features/",
                "ZoomInfo (B2B)": "https://www.zoominfo.com/search/{dado}",
                "Lusha (Contatos)": "https://www.lusha.com/search/?q={dado}",
            },
            "ENDERECO": {
                "Correios (Busca CEP)": "https://buscacepinter.correios.com.br/app/endereco/index.php",
                "Google Maps (Geolocalização)": "https://www.google.com/maps/search/{dado_url}",
                "Street View": "https://www.google.com/maps/place/{dado_url}",
                "Bing Maps": "https://www.bing.com/maps?q={dado_url}",
                "OpenStreetMap": "https://www.openstreetmap.org/search?query={dado_url}",
                "Waze Map Editor": "https://www.waze.com/live-map/directions/{dado_url}",
                "Registro de Imóveis (Cartório)": "https://registradores.onrbrasil.com.br/",
                "Sinduscon (Obras)": "https://www.sindusconsp.com.br/",
                "IPTU Online (Consulta)": "https://iptu.prefeitura.sp.gov.br/",
                "Google Dork (Contas de Água/Luz)": "https://www.google.com/search?q=%22{dado_url}%22+%22conta%22+%22luz%22+OR+%22%C3%A1gua%22+ext%3Apdf",
                "Wikimapia": "https://wikimapia.org/#lang=pt&q={dado_url}",
                "Radar CNJ (Registros Públicos)": "https://radarcnj.cnj.jus.br/registros",
            },
            "PLACA_VEICULO": {
                "Consulta Placa (Detran)": "https://consultaplacas.com.br/consulta-placa-veiculo/{dado}",
                "Placa Fipe": "https://placafipe.com/consulta-placa/{dado}",
                "Consulta Placa (Tabela FIPE)": "https://veiculos.fipe.org.br/",
                "Detran SP (Consulta Débitos)": "https://www.detran.sp.gov.br/",
                "Detran RJ (Consulta)": "https://www.detran.rj.gov.br/",
                "Detran MG (Consulta)": "https://www.detran.mg.gov.br/",
                "Detran RS (Consulta)": "https://www.detran.rs.gov.br/",
                "Sinesp Cidadão (App)": "https://www.sinesp.gov.br/",
                "IPVA (Consulta)": "https://ipva.fazenda.sp.gov.br/",
                "Leilão de Veículos": "https://www.leiloes.com.br/busca?q={dado}",
                "Alienação Fiduciária": "https://www.consultaremovida.com.br/",
            },
            "PROCESSO_JUDICIAL": {
                "CNJ (Consulta Pública)": "https://consultaprocessual.cnj.jus.br/consultaprocessual/",
                "JusBrasil (Número Único)": "https://www.jusbrasil.com.br/processos/{dado}",
                "Escavador (Processo)": "https://www.escavador.com/busca-processos/{dado}",
                "PJe (Consulta Pública)": "https://pje.jus.br/consultapublica/",
                "TRF (Justiça Federal)": "https://www.trf.jus.br/consulta-processual/",
                "TJ (Justiça Estadual)": "https://www.tj.jus.br/consulta-processual/",
                "STJ (Superior Tribunal)": "https://processo.stj.jus.br/",
                "STF (Supremo Tribunal)": "https://portal.stf.jus.br/processos/",
                "TST (Trabalhista)": "https://www.tst.jus.br/consultas-judiciais",
                "TRE (Eleitoral)": "https://www.tse.jus.br/servicos-judiciais/processos",
            },
        }

    def gerar_dossie_links(self, tipo_dado, valor):
        """
        Retorna uma lista de strings com os links úteis para o dado pesquisado.
        tipo_dado pode ser: 'CPF', 'CNPJ', 'NOME', 'TELEFONE', 'EMAIL', 'ENDERECO', 'PLACA_VEICULO', 'PROCESSO_JUDICIAL'
        """
        if tipo_dado not in self.fontes:
            return []
            
        links = []
        
        # Limpeza do valor baseado no tipo
        if tipo_dado == "CPF":
            valor_limpo = "".join(filter(str.isdigit, valor))
        elif tipo_dado == "CNPJ":
            valor_limpo = "".join(filter(str.isdigit, valor))
        elif tipo_dado == "TELEFONE":
            valor_limpo = "".join(filter(str.isdigit, valor))
        elif tipo_dado == "EMAIL":
            valor_limpo = valor.lower().strip()
        elif tipo_dado == "PLACA_VEICULO":
            valor_limpo = valor.upper().replace("-", "").strip()
        else:
            valor_limpo = "".join(filter(str.isalnum, valor)) if tipo_dado in ["CPF", "CNPJ"] else valor
            
        valor_url = urllib.parse.quote(valor)
        
        for nome_fonte, template in self.fontes[tipo_dado].items():
            try:
                url = template.format(dado=valor_limpo, dado_url=valor_url)
                links.append(f"- {nome_fonte}: {url}")
            except KeyError:
                # Fallback caso o template espera apenas {dado}
                try:
                    url = template.format(dado=valor_limpo)
                    links.append(f"- {nome_fonte}: {url}")
                except:
                    url = template
                    links.append(f"- {nome_fonte}: {url}")
                    
        return links
    
    def listar_tipos_disponiveis(self):
        """Retorna lista de tipos de dados suportados"""
        return list(self.fontes.keys())
    
    def buscar_todas_fontes(self, valor, tipos=None):
        """
        Busca em múltiplos tipos de fonte.
        tipos: lista de tipos ('CPF', 'CNPJ', etc.) ou None para todos
        """
        if tipos is None:
            tipos = self.listar_tipos_disponiveis()
            
        resultados = {}
        for tipo in tipos:
            if tipo in self.fontes:
                resultados[tipo] = self.gerar_dossie_links(tipo, valor)
        return resultados