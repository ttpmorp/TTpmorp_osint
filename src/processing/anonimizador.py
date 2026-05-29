import re
import hashlib

class Anonimizador:
    def __init__(self):
        # Regex para CPF Brasileiro (XXX.XXX.XXX-XX ou XXXXXXXXXXX)
        self.padrao_cpf = re.compile(r'\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b')
        # Regex básico para E-mail
        self.padrao_email = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b')
        # Regex básico para Telefone (Formato Brasileiro)
        self.padrao_telefone = re.compile(r'\(?\d{2}\)?\s?(?:9\d{4}|[2-8]\d{3})-?\d{4}\b')

    def _hashear_dados(self, correspondencia):
        """Substitui a string correspondente pelo seu prefixo de hash SHA-256 para manter os relacionamentos."""
        dados = correspondencia.group(0)
        valor_hash = hashlib.sha256(dados.encode()).hexdigest()[:12]
        return f"[ANONIMIZADO:{valor_hash}]"

    def anonimizar_texto(self, texto):
        """
        Encontra e anonimiza dados sensíveis (CPF, E-mail, Telefone) no texto.
        Substitui-os por um hash para que o mesmo CPF sempre gere o mesmo hash,
        permitindo rastreamento sem armazenar o CPF real.
        """
        if not texto:
            return ""
            
        texto = self.padrao_cpf.sub(self._hashear_dados, texto)
        texto = self.padrao_email.sub(self._hashear_dados, texto)
        texto = self.padrao_telefone.sub(self._hashear_dados, texto)
        return texto

    def anonimizar_string(self, valor):
        """Hashea um único valor em string diretamente."""
        if not valor: return None
        return hashlib.sha256(valor.encode()).hexdigest()
