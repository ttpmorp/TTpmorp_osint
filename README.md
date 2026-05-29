# 🕵️‍♂️ Sistema OSINT Avançado - Brasil

Um sistema modular e extensível para **Inteligência de Fontes Abertas (OSINT)** focado no Brasil. Ele automatiza a extração, processamento e armazenamento de dados públicos sobre Pessoas Físicas e Jurídicas, auxiliando investigações e due diligence através do intercruzamento de dados.

## 🚀 Funcionalidades

- **Coleta Automatizada**: Extração de dados textuais e consultas a APIs abertas (como a [Brasil API](https://brasilapi.com.br/)).
- **Processamento NLP**: Utiliza Inteligência Artificial (spaCy) para identificar e extrair Nomes, Organizações e Localidades de textos brutos.
- **Anonimização de Dados Sensíveis**: Mascaramento via hash de CPF, E-mail e Telefone antes de persistir no banco, garantindo segurança operacional.
- **Enriquecimento Dinâmico (Pivotamento)**: Descobriu um CNPJ no texto? O sistema consulta automaticamente quem são os sócios, a razão social, e checa pendências/sanções no Portal da Transparência da CGU.
- **Catálogo Inteligente**: Geração dinâmica de "Dossiês de Links", injetando o CPF/CNPJ alvo em dezenas de portais governamentais e ferramentas de busca (JusBrasil, Escavador, Receita Federal) para facilitar a investigação manual avançada.
- **Orquestração**: Tarefas gerenciadas via Prefect para robustez e monitoramento.
- **Armazenamento Seguro**: Persistência usando SQLAlchemy (PostgreSQL / SQLite).

## 🛠️ Tecnologias Utilizadas

- **Linguagem**: Python 3.x
- **Scraping**: BeautifulSoup4, Requests
- **NLP / IA**: spaCy (`pt_core_news_sm`)
- **Orquestração**: Prefect
- **Banco de Dados**: SQLAlchemy, PostgreSQL (via Docker) e SQLite (fallback local)

## ⚙️ Como Instalar

1. **Clone e acesse o diretório do projeto**
2. **Crie e ative o ambiente virtual:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   ```
3. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   python -m spacy download pt_core_news_sm
   ```
4. **Suba o Banco de Dados (Opcional, o SQLite é usado como fallback):**
   ```bash
   docker-compose up -d
   ```

## ▶️ Como Usar

O fluxo principal (orquestrador) pode ser chamado diretamente pelo terminal, passando o nome da pessoa alvo ou um CNPJ.

**Buscando por uma Pessoa (Exemplo):**
```bash
python src/orchestration/fluxo_principal.py --pessoa "Nome Completo do Alvo"
```

**Buscando por uma Empresa/CNPJ (Exemplo):**
```bash
python src/orchestration/fluxo_principal.py --cnpj "00000000000191"
```

### O que o sistema fará?
1. Irá consultar fontes e baixar o texto bruto.
2. Identificará (via Regex) qualquer CNPJ, CEP ou DDD e fará chamadas extras para enriquecer esses dados (Ex: Descobrir de qual estado é o telefone).
3. Processará os nomes associados usando NLP.
4. Salvará no Banco de Dados a "Teia de Relações" do Alvo.
5. Imprimirá no terminal um **Dossiê Dinâmico** com dezenas de links formatados para você clicar e continuar a investigação visualmente.

## 🔑 Configurações Avançadas (.env)

Para usar algumas APIs restritas, crie um arquivo `.env` na raiz do projeto:
- `CGU_API_KEY=sua_chave_aqui` : Libera a consulta de sanções e processos no Portal da Transparência.
- `DATABASE_URL=postgresql://...` : Força o uso do PostgreSQL em vez do SQLite.

---
**Aviso Legal:** *Este sistema tem fins educacionais e de pesquisa de segurança. O scraping e uso de dados abertos deve sempre respeitar os termos de uso dos sites alvo e as legislações vigentes (LGPD).*
