# 🗂️ Arquitetura e Estratégia de Dados OSINT

Este documento descreve como o **Sistema OSINT Avançado** processa as fontes de inteligência, lida com a volatilidade da web (captchas, bloqueios) e como utiliza seu catálogo expansível para guiar investigações.

## 1. O Desafio da Coleta em Portais Governamentais
Portais brasileiros como *Receita Federal*, *Meu INSS*, *Portal de Processos (PJe)*, e *Detrans* implementam bloqueios severos contra automação (Cloudflare, reCAPTCHA, exigência de Certificado Digital Gov.br). Criar *scrapers* que navegam nesses sites torna a manutenção do código um pesadelo constante.

A solução adotada pelo nosso ecossistema baseia-se em **Duas Camadas**:

### Camada 1: Automação Total (APIs e Dados Estruturados)
Toda a parte que não exige quebra de captcha é feita de forma autônoma (sem intervenção do usuário):
- **Brasil API**: Intercruzamento e descoberta de sócios, validação de CEP e DDD.
- **Portal da Transparência CGU (via API)**: Utilizando a chave da CGU, o sistema verifica antecedentes ("Ficha Suja", processos de corrupção ou empresas inidôneas sancionadas).
- **Processamento NLP**: Varredura de textos públicos em busca de fragmentos sensíveis com spaCy e Expressões Regulares (Regex) para garimpar padrões de documentos ocultos na web.

### Camada 2: Inteligência Humana Guiada (O "Catálogo OSINT")
A segunda etapa é a geração do **Dossiê Dinâmico**. Ao invés de o robô tentar quebrar o captcha do *JusBrasil* e ser bloqueado, o sistema pega os CPFs, CNPJs e Nomes extraídos da *Camada 1* e utiliza o módulo `catalogo_fontes.py` para gerar uma lista de "Links Injetados".

## 2. Fontes OSINT Mapeadas no Catálogo Atual

O sistema atualmente conhece e mapeia as seguintes entidades para Pivotamento rápido:

### 🔎 Busca por CNPJ
- **Receita Federal (Situação Cadastral)**
- **Portal da Transparência CGU (Sanções / CEIS / CNEP)**
- **JusBrasil (Processos Judiciais da Empresa)**
- **RedeCNPJ (Gráficos Societários Visuais)**

### 🔎 Busca por Nome (Pessoa Física)
- **JusBrasil (Descobrir bens em litígio e processos)**
- **Escavador (Processos Trabalhistas e Diários Oficiais)**
- **Portal da Transparência (Buscar Salários de Servidores Federais e Viagens)**
- **TRF (Tribunais Regionais Federais - Portal de Precatórios)**
- **Lattes (Bolsas e Histórico Acadêmico via CNPq)**
- **LinkedIn (Pivotamento corporativo)**
- **Google Dorks (Automação de Dorks de busca por PDFs/XLSX expostos contendo o nome)**

### 🔎 Busca por CPF
- **Receita Federal**
- **TSE (Certidão de Quitação Eleitoral e Crimes Eleitorais)**
- **Banco Central (Valores a Receber - SVR)**

## 3. Fluxo de Enriquecimento e "Pivotamento"

O termo *Pivotamento* significa usar uma informação descoberta para descobrir outra. No nosso código, funciona assim:

1. A pesquisa começa com o alvo principal: Ex: `Marcos Silva`.
2. Durante o processamento do texto sobre Marcos, o módulo `extrator_padroes.py` fisga a *string* `19.131.243/0001-97`.
3. O orquestrador pega essa *string* recém descoberta, a joga contra a **Brasil API** e descobre que se trata do CNPJ de uma Tech. 
4. O orquestrador salva a relação de que Marcos está ligado a essa Tech no Banco de Dados (`RelacaoEntidade`).
5. O orquestrador joga esse CNPJ recém-descoberto contra a **API da CGU**, e descobre se há fraudes na empresa ligada ao Marcos.
6. O terminal encerra te entregando todos os links do *JusBrasil* para você investigar manualmente não apenas o Marcos, mas a empresa vinculada a ele!

## 4. Como Adicionar Novas Fontes

Para adicionar uma das centenas de fontes da *Megabase OSINT Brasileira* ao nosso sistema de geração de links, basta atualizar o arquivo `src/collectors/catalogo_fontes.py`.

**Exemplo:**
Se você quiser adicionar o *Radar Siscomex* para CNPJs, basta adicionar no dicionário de CNPJ do código:
```python
"Radar Siscomex": "https://www.gov.br/receitafederal/pt-br/assuntos/aduana/.../{dado}"
```
Com uma única linha, todos os CNPJs encontrados dali em diante passarão a gerar atalhos automáticos para pesquisa de exportação do Siscomex.
