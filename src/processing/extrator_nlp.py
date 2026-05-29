import spacy

class ExtratorNLP:
    def __init__(self, nome_modelo="pt_core_news_sm"):
        """
        Inicializa o Extrator NLP.
        Requer que o modelo do spaCy esteja baixado:
        python -m spacy download pt_core_news_sm
        """
        try:
            self.nlp = spacy.load(nome_modelo)
            print(f"[*] Modelo spaCy carregado: {nome_modelo}")
        except OSError:
            print(f"[-] Modelo {nome_modelo} não encontrado. Por favor, execute: python -m spacy download {nome_modelo}")
            self.nlp = None

    def extrair_entidades(self, texto):
        """
        Extrai Entidades Nomeadas (PER/Pessoas, ORG/Organizações, LOC/Localidades) do texto.
        Retorna um dicionário agrupando as entidades pelo rótulo.
        """
        if not self.nlp or not texto:
            return {"PER": [], "ORG": [], "LOC": []}

        doc = self.nlp(texto)
        entidades = {"PER": set(), "ORG": set(), "LOC": set()}
        
        for ent in doc.ents:
            if ent.label_ in entidades:
                entidades[ent.label_].add(ent.text.strip())
                
        # Converte os sets de volta para listas para facilitar a serialização
        return {k: list(v) for k, v in entidades.items()}

    def extrair_relacoes(self, texto):
        """
        Exemplo básico de extração de relações (PoC Didática).
        Em um sistema real, usaríamos parsing de dependência ou um modelo
        customizado para encontrar ligações como (Pessoa) -> [Trabalha Em] -> (Organização).
        """
        # Para esta PoC, vamos apenas confiar nas entidades extraídas
        # e assumir que estão relacionadas à pessoa principal pesquisada.
        pass
