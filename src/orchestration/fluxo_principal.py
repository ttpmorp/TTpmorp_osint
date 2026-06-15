import sys
import os

# Adiciona o diretório pai ao path do Python para que as importações funcionem corretamente
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from prefect import flow, task
from src.collectors.coletor_academico import ColetorAcademico
from src.collectors.coletor_brasil_api import ColetorBrasilAPI
from src.collectors.coletor_transparencia_cgu import ColetorTransparenciaCGU
from src.collectors.coletor_redes_sociais import ColetorRedesSociais
from src.collectors.catalogo_fontes import CatalogoFontesOSINT
from src.processing.extrator_nlp import ExtratorNLP
from src.processing.anonimizador import Anonimizador
from src.processing.extrator_padroes import ExtratorPadroes
from src.database.cliente_bd import ClienteBD
from src.database.modelos import Pessoa, RelacaoEntidade, DadosBrutos

@task(retries=2, retry_delay_seconds=5)
def coletar_dados_pessoa(nome_pessoa: str) -> str:
    print(f"[*] Iniciando coleta para a pessoa: {nome_pessoa}")
    coletor = ColetorAcademico()
    texto = coletor.buscar_pessoa(nome_pessoa)
    return texto

@task(retries=2, retry_delay_seconds=5)
def coletar_dados_empresa(cnpj: str) -> dict:
    print(f"[*] Iniciando coleta para a empresa (CNPJ): {cnpj}")
    coletor = ColetorBrasilAPI()
    dados = coletor.buscar_cnpj(cnpj)
    return dados

@task
def processar_dados_texto(texto: str) -> dict:
    print("[*] Processando dados de texto e extraindo padrões...")
    if not texto:
        return {"texto_anonimizado": "", "entidades": {}, "padroes": {}}
        
    extrator_padroes = ExtratorPadroes()
    anonimizador = Anonimizador()
    extrator_nlp = ExtratorNLP()
    
    # Extrair CNPJs, CEPs, e DDDs ANTES de anonimizar
    padroes = extrator_padroes.extrair(texto)
    
    # Anonimizar texto
    texto_anonimizado = anonimizador.anonimizar_texto(texto)
    
    # Extrair entidades via NLP no texto anonimizado
    entidades = extrator_nlp.extrair_entidades(texto_anonimizado)
    
    return {
        "texto_anonimizado": texto_anonimizado,
        "entidades": entidades,
        "padroes": padroes
    }

@task
def salvar_no_banco_pessoa(nome_pessoa: str, dados_processados: dict, url_origem: str):
    print("[*] Salvando dados da pessoa no banco...")
    db = ClienteBD()
    db.iniciar_bd()
    sessao = db.obter_sessao()
    pessoa_id = None
    
    try:
        pessoa = sessao.query(Pessoa).filter_by(nome=nome_pessoa).first()
        if not pessoa:
            pessoa = Pessoa(nome=nome_pessoa, metadados_json={})
            sessao.add(pessoa)
            sessao.flush()
        
        pessoa_id = pessoa.id
        
        if dados_processados["texto_anonimizado"]:
            bruto = DadosBrutos(
                pessoa_id=pessoa.id,
                url_origem=url_origem,
                conteudo_anonimizado=dados_processados["texto_anonimizado"]
            )
            sessao.add(bruto)
            
        entidades = dados_processados["entidades"]
        relacoes_existentes = {(r.tipo_entidade, r.nome_entidade) for r in pessoa.relacoes}
        
        for tipo_e in ["ORG", "LOC"]: 
            for nome_e in entidades.get(tipo_e, []):
                if (tipo_e, nome_e) not in relacoes_existentes:
                    rel = RelacaoEntidade(pessoa_id=pessoa.id, tipo_entidade=tipo_e, nome_entidade=nome_e)
                    sessao.add(rel)
                    relacoes_existentes.add((tipo_e, nome_e))
        
        sessao.commit()
        print(f"[+] Salvo com sucesso no banco. Pessoa ID: {pessoa_id}")
        return pessoa_id
    except Exception as e:
        sessao.rollback()
        print(f"[-] Erro no Banco de Dados: {e}")
        return None
    finally:
        sessao.close()

@task
def enriquecer_com_brasil_api(pessoa_id: int, padroes: dict):
    if not pessoa_id or not padroes: return
    
    print("[*] Iniciando enriquecimento de dados via Brasil API...")
    coletor = ColetorBrasilAPI()
    db = ClienteBD()
    sessao = db.obter_sessao()
    
    try:
        pessoa = sessao.query(Pessoa).get(pessoa_id)
        relacoes_existentes = {(r.tipo_entidade, r.nome_entidade) for r in pessoa.relacoes}
        
        # 1. Enriquecer DDD (Região do Telefone)
        for ddd in padroes.get("ddds", []):
            dados_ddd = coletor.buscar_ddd(ddd)
            if dados_ddd and "state" in dados_ddd:
                estado = dados_ddd["state"]
                if ("ESTADO_DDD", estado) not in relacoes_existentes:
                    rel = RelacaoEntidade(pessoa_id=pessoa.id, tipo_entidade="ESTADO_DDD", nome_entidade=f"{estado} (DDD {ddd})")
                    sessao.add(rel)
                    relacoes_existentes.add(("ESTADO_DDD", estado))
                    print(f"  -> Encontrado Estado pelo DDD: {estado}")
                    
        # 2. Enriquecer CEP
        for cep in padroes.get("ceps", []):
            dados_cep = coletor.buscar_cep(cep)
            if dados_cep and "city" in dados_cep:
                cidade_estado = f"{dados_cep['city']}/{dados_cep['state']}"
                if ("LOCALIZACAO_CEP", cidade_estado) not in relacoes_existentes:
                    rel = RelacaoEntidade(pessoa_id=pessoa.id, tipo_entidade="LOCALIZACAO_CEP", nome_entidade=f"{cidade_estado} (CEP {cep})")
                    sessao.add(rel)
                    relacoes_existentes.add(("LOCALIZACAO_CEP", cidade_estado))
                    print(f"  -> Encontrada Localização pelo CEP: {cidade_estado}")

        # 3. Enriquecer CNPJ (Brasil API e CGU)
        cgu = ColetorTransparenciaCGU()
        for cnpj in padroes.get("cnpjs", []):
            dados_cnpj = coletor.buscar_cnpj(cnpj)
            if dados_cnpj and "razao_social" in dados_cnpj:
                empresa = dados_cnpj["razao_social"]
                if ("EMPRESA_CNPJ", empresa) not in relacoes_existentes:
                    rel = RelacaoEntidade(pessoa_id=pessoa.id, tipo_entidade="EMPRESA_CNPJ", nome_entidade=f"{empresa} (CNPJ {cnpj})")
                    sessao.add(rel)
                    relacoes_existentes.add(("EMPRESA_CNPJ", empresa))
                    print(f"  -> Encontrada Empresa pelo CNPJ: {empresa}")
                    
                # Busca sanções na CGU
                sancoes = cgu.buscar_sancoes_por_cnpj(cnpj)
                if sancoes:
                    rel_sancao = RelacaoEntidade(pessoa_id=pessoa.id, tipo_entidade="ALERTA_SANCAO_CGU", nome_entidade=f"Sanção aplicada a {empresa}")
                    sessao.add(rel_sancao)

        sessao.commit()
        print("[+] Enriquecimento concluído com sucesso!")
        
    except Exception as e:
        sessao.rollback()
        print(f"[-] Erro ao enriquecer dados no Banco de Dados: {e}")
    finally:
        sessao.close()

@task
def salvar_no_banco_empresa(dados_empresa: dict):
    if not dados_empresa: return
        
    print("[*] Salvando dados da empresa no banco...")
    db = ClienteBD()
    db.iniciar_bd()
    sessao = db.obter_sessao()
    
    try:
        razao_social = dados_empresa.get("razao_social", "Empresa Desconhecida")
        
        empresa = sessao.query(Pessoa).filter_by(nome=razao_social).first()
        if not empresa:
            empresa = Pessoa(nome=razao_social, metadados_json=dados_empresa)
            sessao.add(empresa)
            sessao.flush()
            
        socios = dados_empresa.get("qsa", [])
        for socio in socios:
            nome_socio = socio.get("nome_socio")
            if nome_socio:
                rel = RelacaoEntidade(pessoa_id=empresa.id, tipo_entidade="SOCIO", nome_entidade=nome_socio)
                sessao.add(rel)
                
        sessao.commit()
        print(f"[+] Empresa {razao_social} salva com {len(socios)} sócios.")
    except Exception as e:
        sessao.rollback()
        print(f"[-] Erro no Banco de Dados: {e}")
    finally:
        sessao.close()


@task
def exibir_detalhes_cnpj(dados: dict):
    """Exibe um relatório completo e formatado dos dados de CNPJ retornados pela Brasil API."""
    if not dados:
        return
    sep = "=" * 60
    print(f"\n{sep}")
    print("   RELATÓRIO COMPLETO - CNPJ")
    print(sep)
    print(f"  CNPJ                : {dados.get('cnpj', 'N/A')}")
    print(f"  Razão Social        : {dados.get('razao_social', 'N/A')}")
    print(f"  Nome Fantasia       : {dados.get('nome_fantasia') or 'N/A'}")
    print(f"  Situação Cadastral  : {dados.get('descricao_situacao_cadastral', 'N/A')}")
    print(f"  Data Abertura       : {dados.get('data_inicio_atividade', 'N/A')}")
    print(f"  Natureza Jurídica   : {dados.get('natureza_juridica', 'N/A')}")
    print(f"  Porte               : {dados.get('porte', 'N/A')}")
    print(f"  Capital Social      : R$ {dados.get('capital_social', 0):,.2f}")
    print(f"  Tipo                : {dados.get('descricao_identificador_matriz_filial', 'N/A')}")

    print(f"\n  --- ENDEREÇO ---")
    logr = f"{dados.get('descricao_tipo_de_logradouro', '')} {dados.get('logradouro', '')}, {dados.get('numero', '')}"
    print(f"  Logradouro          : {logr.strip()}")
    if dados.get('complemento'):
        print(f"  Complemento         : {dados.get('complemento')}")
    print(f"  Bairro              : {dados.get('bairro', 'N/A')}")
    print(f"  Município / UF      : {dados.get('municipio', 'N/A')} / {dados.get('uf', 'N/A')}")
    print(f"  CEP                 : {dados.get('cep', 'N/A')}")

    print(f"\n  --- CONTATO ---")
    print(f"  Telefone 1          : {dados.get('ddd_telefone_1') or 'N/A'}")
    print(f"  Telefone 2          : {dados.get('ddd_telefone_2') or 'N/A'}")
    print(f"  E-mail              : {dados.get('email') or 'N/A'}")

    print(f"\n  --- ATIVIDADE ECONÔMICA ---")
    print(f"  CNAE Principal      : {dados.get('cnae_fiscal', 'N/A')} - {dados.get('cnae_fiscal_descricao', 'N/A')}")
    cnaes_sec = dados.get('cnaes_secundarios', [])
    if cnaes_sec:
        print(f"  CNAEs Secundários   :")
        for cnae in cnaes_sec:
            print(f"    - {cnae.get('codigo')} - {cnae.get('descricao')}")

    print(f"\n  --- REGIME TRIBUTÁRIO ---")
    regimes = dados.get('regime_tributario', [])
    if regimes:
        for r in regimes:
            print(f"    {r.get('ano')}: {r.get('forma_de_tributacao')}")
    else:
        simples = "Sim" if dados.get('opcao_pelo_simples') else "Não"
        mei = "Sim" if dados.get('opcao_pelo_mei') else "Não"
        print(f"  Simples Nacional    : {simples}")
        print(f"  MEI                 : {mei}")

    print(f"\n  --- QUADRO SOCIETÁRIO (QSA) ---")
    qsa = dados.get('qsa', [])
    if qsa:
        for i, socio in enumerate(qsa, 1):
            print(f"  [{i}] {socio.get('nome_socio', 'N/A')}")
            print(f"       Qualificação : {socio.get('qualificacao_socio', 'N/A')}")
            print(f"       Faixa Etária : {socio.get('faixa_etaria', 'N/A')}")
            print(f"       Desde        : {socio.get('data_entrada_sociedade', 'N/A')}")
    else:
        print("  Nenhum sócio encontrado.")
    print(sep + "\n")


@task
def exibir_dossie_links(nome_pessoa: str, cnpjs: list = None):
    print(f"\n{'='*40}\n[+] Dossiê de Links Rápidos para Investigação Manual\n{'='*40}")
    catalogo = CatalogoFontesOSINT()
    
    # Links por Nome
    links_nome = catalogo.gerar_dossie_links("NOME", nome_pessoa)
    for link in links_nome:
        print(link)
        
    # Links por CNPJs associados
    if cnpjs:
        print("\n[+] Links para Empresas Encontradas:")
        for cnpj in cnpjs:
            links_cnpj = catalogo.gerar_dossie_links("CNPJ", cnpj)
            for link in links_cnpj:
                print(link)
    print("="*40)

@flow(name="Pipeline-OSINT-Pessoa")
def pipeline_osint_pessoa(nome_pessoa: str):
    print(f"\n{'='*40}\nIniciando Pipeline OSINT para Pessoa: {nome_pessoa}\n{'='*40}")
    
    texto_bruto = coletar_dados_pessoa(nome_pessoa)
    if not texto_bruto:
        print("[-] Nenhum dado encontrado para processar. Encerrando pipeline.")
        return
        
    dados_processados = processar_dados_texto(texto_bruto)
    url_origem = f"https://pt.wikipedia.org/wiki/{nome_pessoa.replace(' ', '_')}"
    
    pessoa_id = salvar_no_banco_pessoa(nome_pessoa, dados_processados, url_origem)
    
    # Passo de Enriquecimento
    padroes_extraidos = dados_processados.get("padroes", {})
    enriquecer_com_brasil_api(pessoa_id, padroes_extraidos)
    
    # Passo Final: Exibe links de investigação manual baseados no gigantesco catálogo OSINT
    exibir_dossie_links(nome_pessoa, cnpjs=padroes_extraidos.get("cnpjs", []))
    
    print("\n[+] Execução do pipeline de pessoa concluída.")

@flow(name="Pipeline-OSINT-Empresa")
def pipeline_osint_empresa(cnpj: str):
    print(f"\n{'='*40}\nIniciando Pipeline OSINT para Empresa (CNPJ): {cnpj}\n{'='*40}")
    
    dados_empresa = coletar_dados_empresa(cnpj)
    if not dados_empresa:
        print("[-] Nenhum dado de empresa encontrado. Encerrando pipeline.")
        return
    
    # Exibe relatório completo antes de salvar
    exibir_detalhes_cnpj(dados_empresa)
    salvar_no_banco_empresa(dados_empresa)
    
    # Exibe dossiê de links para a empresa
    exibir_dossie_links(dados_empresa.get("razao_social", ""), cnpjs=[cnpj])
    
    print("\n[+] Execução do pipeline de empresa concluída.")


# ======================================================================
#  Pipeline OSINT - Busca por Nome de Usuário (Redes Sociais)
# ======================================================================

@task(retries=2, retry_delay_seconds=5)
def coletar_redes_sociais(usuario: str) -> list:
    print(f"[*] Verificando redes sociais para o usuário: @{usuario}")
    coletor = ColetorRedesSociais()
    resultados = coletor.verificar_usuario(usuario)
    return resultados

@task
def salvar_no_banco_usuario(usuario: str, resultados: list):
    print("[*] Salvando resultados de redes sociais no banco...")
    db = ClienteBD()
    db.iniciar_bd()
    sessao = db.obter_sessao()

    try:
        pessoa = sessao.query(Pessoa).filter_by(nome=f"@{usuario}").first()
        if not pessoa:
            pessoa = Pessoa(nome=f"@{usuario}", metadados_json={"tipo": "usuario"})
            sessao.add(pessoa)
            sessao.flush()

        relacoes_existentes = {(r.tipo_entidade, r.nome_entidade) for r in pessoa.relacoes}

        for r in resultados:
            if r["encontrado"]:
                tipo = "REDE_SOCIAL"
                nome_ent = f"{r['plataforma']} - {r['url']}"
                if (tipo, nome_ent) not in relacoes_existentes:
                    rel = RelacaoEntidade(
                        pessoa_id=pessoa.id,
                        tipo_entidade=tipo,
                        nome_entidade=nome_ent,
                    )
                    sessao.add(rel)
                    relacoes_existentes.add((tipo, nome_ent))

        sessao.commit()
        print(f"[+] Resultados de @{usuario} salvos no banco. Pessoa ID: {pessoa.id}")
        return pessoa.id
    except Exception as e:
        sessao.rollback()
        print(f"[-] Erro no Banco de Dados: {e}")
        return None
    finally:
        sessao.close()

@task
def exibir_relatorio_redes_sociais(usuario: str, resultados: list):
    """Exibe um relatório formatado das redes sociais encontradas."""
    sep = "=" * 60
    print(f"\n{sep}")
    print(f"   RELATÓRIO DE REDES SOCIAIS - @{usuario}")
    print(sep)

    encontrados = [r for r in resultados if r["encontrado"]]
    nao_encontrados = [r for r in resultados if not r["encontrado"]]

    print(f"\n  Total verificado : {len(resultados)}")
    print(f"  Encontrados      : {len(encontrados)}")
    print(f"  Não encontrados  : {len(nao_encontrados)}")

    if encontrados:
        print(f"\n  --- PERFIS ENCONTRADOS ---")
        for i, r in enumerate(encontrados, 1):
            print(f"  [{i:>2}] {r['plataforma']:<20} {r['url']}")
    else:
        print("\n  Nenhum perfil encontrado.")

    print(f"\n{sep}\n")

@task
def exibir_dossie_links_usuario(usuario: str):
    """Exibe links de investigação manual para o nome de usuário."""
    print(f"\n{'='*40}")
    print(f"[+] Dossiê de Links Rápidos para o Usuário @{usuario}")
    print(f"{'='*40}")
    catalogo = CatalogoFontesOSINT()
    links = catalogo.gerar_dossie_links("USUARIO", usuario)
    for link in links:
        print(link)
    print("="*40)

@flow(name="Pipeline-OSINT-Usuario")
def pipeline_osint_usuario(usuario: str):
    usuario = usuario.strip().lstrip("@")
    print(f"\n{'='*40}")
    print(f"Iniciando Pipeline OSINT para Usuário: @{usuario}")
    print(f"{'='*40}")

    resultados = coletar_redes_sociais(usuario)
    salvar_no_banco_usuario(usuario, resultados)
    exibir_relatorio_redes_sociais(usuario, resultados)
    exibir_dossie_links_usuario(usuario)

    print("\n[+] Execução do pipeline de usuário concluída.")

BANNER_OSINT = r"""
$$$$$$$$\ $$$$$$$$\                                                    
\__$$  __|\__$$  __|                                                   
   $$ |      $$ | $$$$$$\  $$$$$$\$$$$\   $$$$$$\   $$$$$$\   $$$$$$\  
   $$ |      $$ |$$  __$$\ $$  _$$  _$$\ $$  __$$\ $$  __$$\ $$  __$$\ 
   $$ |      $$ |$$ /  $$ |$$ / $$ / $$ |$$ /  $$ |$$ |  \__|$$ /  $$ |
   $$ |      $$ |$$ |  $$ |$$ | $$ | $$ |$$ |  $$ |$$ |      $$ |  $$ |
   $$ |      $$ |$$$$$$$  |$$ | $$ | $$ |\$$$$$$  |$$ |      $$$$$$$  |
   \__|      \__|$$  ____/ \__| \__| \__| \______/ \__|      $$  ____/ 
                 $$ |                                        $$ |      
                 $$ |                                        $$ |      
                 \__|                                        \__|                                                                                                       
"""

def menu_interativo():
    print(BANNER_OSINT)
    
    while True:
        print("\n" + "="*50)
        print(" 🕵️‍♂️  SISTEMA OSINT AVANÇADO - MODO INTERATIVO")
        print("="*50 + "\n")
        print("Selecione o tipo de entidade que deseja investigar:")
        print("  [ 1 ] Pessoa Física (Busca por Nome)")
        print("  [ 2 ] Empresa (Busca por CNPJ)")
        print("  [ 3 ] Redes Sociais (Busca por Nome de Usuário)")
        print("  [ 0 ] Sair")
        
        escolha = input("\n> Digite o número da sua escolha: ").strip()
        
        if escolha == '1':
            nome = input("\n> Digite o Nome da pessoa (ex: 'Albert Einstein'): ").strip()
            if nome:
                pipeline_osint_pessoa(nome)
            else:
                print("[-] O nome não pode ser vazio.")
        elif escolha == '2':
            cnpj = input("\n> Digite o CNPJ da empresa (apenas números): ").strip()
            if cnpj:
                pipeline_osint_empresa(cnpj)
            else:
                print("[-] O CNPJ não pode ser vazio.")
        elif escolha == '3':
            usuario = input("\n> Digite o nome de usuário (ex: 'johndoe'): ").strip()
            if usuario:
                pipeline_osint_usuario(usuario)
            else:
                print("[-] O nome de usuário não pode ser vazio.")
        elif escolha == '0':
            print("\nSaindo do sistema. Até a próxima investigação! 👋")
            break
        else:
            print("\n[-] Escolha inválida. Tente novamente.")
            continue
        
        # Após qualquer pesquisa concluída, pergunta se quer continuar
        nova = input("\nDeseja fazer uma nova pesquisa? (s/n): ").strip().lower()
        if nova != 's':
            print("\nEncerrando o sistema. Até a próxima investigação! 👋")
            break

if __name__ == "__main__":
    import sys
    import argparse
    
    # Se argumentos foram passados na linha de comando, usa o modo CLI
    if len(sys.argv) > 1:
        print(BANNER_OSINT)
        parser = argparse.ArgumentParser(description="Executar PoC do Pipeline OSINT")
        parser.add_argument("--pessoa", type=str, help="Nome da pessoa a pesquisar")
        parser.add_argument("--cnpj", type=str, help="CNPJ da empresa a pesquisar (apenas números)")
        parser.add_argument("--usuario", type=str, help="Nome de usuário para buscar nas redes sociais")
        args = parser.parse_args()
        
        if args.pessoa:
            pipeline_osint_pessoa(args.pessoa)
        elif args.cnpj:
            pipeline_osint_empresa(args.cnpj)
        elif args.usuario:
            pipeline_osint_usuario(args.usuario)
        else:
            print("Por favor, forneça --pessoa 'Nome', --cnpj 'Numero' ou --usuario 'Username'")
    else:
        # Se nenhum argumento foi passado, abre o modo interativo
        menu_interativo()
