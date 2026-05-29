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
            },
            "CPF": {
                "Situação Cadastral Receita Federal": "https://servicos.receita.fazenda.gov.br/Servicos/CPF/ConsultaSituacao/ConsultaPublica.asp",
                "Portal da Transparência (Servidores/Benefícios)": "https://portaldatransparencia.gov.br/busca?termo={dado}",
                "Escavador (Processos e Currículo)": "https://www.escavador.com/busca?q={dado}",
                "TSE - Certidão de Quitação": "https://www.tse.jus.br/servicos-eleitorais/autoatendimento-eleitoral#/certidoes-eleitor/certidao-quitacao-eleitoral",
                "Valores a Receber (Banco Central)": "https://valoresareceber.bcb.gov.br/publico/",
            },
            "NOME": {
                "JusBrasil (Processos)": "https://www.jusbrasil.com.br/consulta-processual/busca?q={dado_url}",
                "Escavador": "https://www.escavador.com/busca?q={dado_url}",
                "Portal da Transparência (Viagens/Salários)": "https://portaldatransparencia.gov.br/busca?termo={dado_url}",
                "Portal de Precatórios (TRF5)": "https://rpvprecatorio.trf5.jus.br/",
                "Lattes (CNPq)": "https://buscatextual.cnpq.br/buscatextual/busca.do",
                "LinkedIn": "https://www.linkedin.com/search/results/all/?keywords={dado_url}",
                "Google Dork (Arquivos)": "https://www.google.com/search?q=%22{dado_url}%22+ext%3Apdf+OR+ext%3Axls",
            }
        }

    def gerar_dossie_links(self, tipo_dado, valor):
        """
        Retorna uma lista de strings com os links úteis para o dado pesquisado.
        tipo_dado pode ser: 'CPF', 'CNPJ' ou 'NOME'.
        """
        if tipo_dado not in self.fontes:
            return []
            
        links = []
        valor_limpo = "".join(filter(str.isalnum, valor)) if tipo_dado in ["CPF", "CNPJ"] else valor
        valor_url = urllib.parse.quote(valor)
        
        for nome_fonte, template in self.fontes[tipo_dado].items():
            url = template.format(dado=valor_limpo, dado_url=valor_url)
            links.append(f"- {nome_fonte}: {url}")
            
        return links
