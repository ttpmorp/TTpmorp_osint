import sys
import os

# Adiciona o diretório pai ao path do Python para que as importações funcionem corretamente
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from prefect import flow, task
from src.collectors.coletor_academico import ColetorAcademico
from src.collectors.coletor_brasil_api import ColetorBrasilAPI
from src.collectors.coletor_transparencia_cgu import ColetorTransparenciaCGU
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
        
    salvar_no_banco_empresa(dados_empresa)
    
    # Exibe dossiê de links para a empresa
    exibir_dossie_links(dados_empresa.get("razao_social", ""), cnpjs=[cnpj])
    
    print("\n[+] Execução do pipeline de empresa concluída.")

BANNER_OSINT = r"""
 [... [......[... [......[.......  [..       [..    [....     [.......    [.......  
     [..         [..    [..    [..[. [..   [...  [..    [..  [..    [..  [..    [..
     [..         [..    [..    [..[.. [.. [ [..[..        [..[..    [..  [..    [..
     [..         [..    [.......  [..  [..  [..[..        [..[. [..      [.......  
     [..         [..    [..       [..   [.  [..[..        [..[..  [..    [..       
     [..         [..    [..       [..       [..  [..     [.. [..    [..  [..       
     [..         [..    [..       [..       [..    [....     [..      [..[..       
                                                                                                      
"""

if __name__ == "__main__":
    print(BANNER_OSINT)
    import argparse
    parser = argparse.ArgumentParser(description="Executar PoC do Pipeline OSINT")
    parser.add_argument("--pessoa", type=str, help="Nome da pessoa a pesquisar (ex: 'Albert Einstein')")
    parser.add_argument("--cnpj", type=str, help="CNPJ da empresa a pesquisar (apenas números)")
    args = parser.parse_args()
    
    if args.pessoa:
        pipeline_osint_pessoa(args.pessoa)
    elif args.cnpj:
        pipeline_osint_empresa(args.cnpj)
    else:
        print("Por favor, forneça --pessoa 'Nome' ou --cnpj 'Numero'")
