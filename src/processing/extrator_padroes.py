import re

class ExtratorPadroes:
    def __init__(self):
        # Regex para CNPJ (com ou sem formatação)
        self.padrao_cnpj = re.compile(r'\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b')
        # Regex para CEP (com ou sem hífen)
        self.padrao_cep = re.compile(r'\b\d{5}-?\d{3}\b')
        # Regex para Telefone com DDD (captura o DDD)
        self.padrao_telefone = re.compile(r'\(?([1-9]{2})\)?\s?(?:9\d{4}|[2-8]\d{3})-?\d{4}\b')

    def extrair(self, texto):
        """
        Extrai CNPJs, CEPs e DDDs de telefones encontrados no texto.
        """
        resultados = {
            "cnpjs": set(),
            "ceps": set(),
            "ddds": set()
        }
        
        if not texto:
            return resultados

        for cnpj in self.padrao_cnpj.findall(texto):
            resultados["cnpjs"].add(cnpj)
            
        for cep in self.padrao_cep.findall(texto):
            resultados["ceps"].add(cep)
            
        for ddd in self.padrao_telefone.findall(texto):
            resultados["ddds"].add(ddd)
            
        # Converte para listas
        return {k: list(v) for k, v in resultados.items()}
