#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FERRAMENTA: RED TEAM AUDITOR PRO - V38.0 (INDUSTRIAL ENGINE)
AUTOR: (@renan_security_researcher)
LOCALIZAÇÃO: RIO DE JANEIRO, BR | 2026
TECNOLOGIA: LLC TECHNOLOGY (LOGIC LLC) | OFFENSIVE SECURITY
AVISO: Uso estritamente educacional e para auditorias autorizadas.
"""

import streamlit as st
import requests
from requests.adapters import HTTPAdapter
import socket
import ssl
import time
import sys
import os
import uuid
import re
import random
import json
import inspect
import threading
import hashlib
import subprocess
from groq import Groq
from fpdf import FPDF
from shodan import Shodan
from modulos.inteligencia import analisar_logs_via_nuvem
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

# --- INICIALIZAÇÃO E AMBIENTE ---
# Carrega as chaves do arquivo .env de forma segura
load_dotenv() 

# --- INICIALIZAÇÃO SEGURA DO SESSION STATE ---
if "wordlist_diretorios" not in st.session_state:
    st.session_state.wordlist_diretorios = ["admin/", "config.php", ".env", "backup.sql"]
if "wordlist_api" not in st.session_state:
    st.session_state.wordlist_api = ["api/v1/users", "v1/config", "swagger.json"]
if "wordlist_nuvem" not in st.session_state:
    st.session_state.wordlist_nuvem = ["storage/", "bucket/", "assets/"]

# Instancia os clientes usando as variáveis de ambiente carregadas
# Exemplo: GROQ_API_KEY e SHODAN_API_KEY configuradas no seu .env
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
shodan_client = Shodan(os.getenv("SHODAN_API_KEY"))

# =====================================================================
# --- I. FUNÇÃO DA IA (Motor na Nuvem) ---
# =====================================================================

import unicodedata
from fpdf import FPDF

def normalizar_texto(texto):
    """Remove acentos e caracteres incompatíveis com o PDF padrão."""
    if not texto:
        return ""
    string_limpa = unicodedata.normalize('NFKD', str(texto)).encode('ASCII', 'ignore').decode('ASCII')
    return string_limpa

def gerar_pdf_relatorio(dados_auditoria, dominio_alvo):
    pdf = FPDF()
    pdf.add_page()
    
    # 1. Cabeçalho
    pdf.set_font("Helvetica", "B", 16)
    titulo = normalizar_texto(f"Relatorio de Auditoria Digital - {dominio_alvo}")
    pdf.cell(0, 10, titulo, ln=True, align="C")
    pdf.ln(5)
    
    # Nível de Risco Geral
    pdf.set_font("Helvetica", "B", 12)
    risco = dados_auditoria.get("nivel_risco_geral", "MEDIO")
    texto_risco = normalizar_texto(f"Classificacao de Risco Geral: {risco}")
    pdf.cell(0, 8, texto_risco, ln=True)
    pdf.ln(3)
    
    # 2. Resumo Executivo
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "1. Resumo Executivo:", ln=True)
    pdf.set_font("Helvetica", "", 10)
    resumo = normalizar_texto(dados_auditoria.get("resumo_executivo", "Nenhum dado fornecido."))
    pdf.multi_cell(0, 6, resumo)
    pdf.ln(5)
    
    # 3. Listagem de Vulnerabilidades
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "2. Vulnerabilidades Analisadas:", ln=True)
    
    vulnerabilidades = dados_auditoria.get("vulnerabilidades_detectadas", [])
    
    for v in vulnerabilidades:
        if isinstance(v, dict):
            pdf.set_font("Helvetica", "B", 11)
            nome_falha = v.get("vulnerabilidade") or v.get("vulnerability") or "Falha Detectada"
            texto_falha = normalizar_texto(f"- {nome_falha}")
            pdf.cell(0, 8, texto_falha, ln=True)
            
            pdf.set_font("Helvetica", "I", 10)
            severidade = normalizar_texto(f"Severidade: {v.get('severidade', 'N/A')}")
            pdf.cell(0, 6, severidade, ln=True)
            
            pdf.set_font("Helvetica", "", 10)
            detalhes = normalizar_texto(f"Detalhes Tecnicos: {v.get('detalhes_tecnicos', '')}")
            mitigacao = normalizar_texto(f"Mitigacao Recomendada: {v.get('mitigacao', '')}")
            
            pdf.multi_cell(190, 6, detalhes)
            pdf.multi_cell(190, 6, mitigacao)
            pdf.ln(4)
        elif isinstance(v, str):
            pdf.set_font("Helvetica", "", 10)
            pdf.multi_cell(190, 6, normalizar_texto(f"- {v}"))
            pdf.ln(2)
            
    # Retorno alinhado com a raiz da função (4 espaços da parede esquerda)
    return pdf.output(dest='S')
# 1. Configurações Globais de Constantes (Imutáveis)
NICK = "renan_security_researcher"
VERSAO = "38.0"
TIMEOUT_GLOBAL = 15

# Desativa avisos de SSL uma única vez no escopo global
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 2. Configuração do Front-End (Streamlit)
st.set_page_config(page_title="Audit Industrial", layout="wide")
st.title(f"🛡️ Industrial Engine v{VERSAO}")

# 3. Gerenciamento de Estado Seguro (Session State)
# Isso garante que cada usuário tenha suas variáveis isoladas na memória
if "url_alvo" not in st.session_state:
    st.session_state.url_alvo = ""

if "shodan_key" not in st.session_state:
    # Tenta puxar do .env primeiro, se não existir, deixa em branco para input manual
    st.session_state.shodan_key = os.getenv('SHODAN_API_KEY', '')

if "hora_inicio" not in st.session_state:
    # Salva a hora exata que o usuário abriu a ferramenta e NUNCA MAIS reseta no clique
    st.session_state.hora_inicio = datetime.now().strftime('%d/%m/%Y %H:%M:%S')

# 4. Controles Dinâmicos de Interface
# O slider atualiza diretamente a variável de estado do usuário atual
st.sidebar.slider("Velocidade (Threads)", 1, 100, key="threads_motor")
# --- FIM DO BLOCO DE INICIALIZAÇÃO ---
# ==============================================================================
# 🎯 RECURSOS TÁTICOS GLOBAIS (Isolados e Otimizados)
# ==============================================================================

# Lista Rotativa de User-Agents (Evita bloqueios e resolve o NameError)
UA_LIST = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1"
]

# Wordlist Estratégica de Diretórios Sensíveis (Direto ao ponto)
WL_DIR = [
    ".env", ".env.old", ".git/config", "admin/", "administrator/", "backup.sql", 
    "backup.zip", "config.php", "config.php.bak", "wp-config.php", "db.sql", 
    "setup.php", "phpinfo.php", "v1/env", ".ssh/id_rsa", "server-status"
]

# Wordlist de Endpoints Críticos de API
WL_API = [
    "api/v1/user", "api/v1/auth", "v2/auth", "swagger.json", "graphQL", 
    "api/status", "internal/v1", "api/v1/debug", "api/docs", "v3/health"
]

# Wordlist de Cloud e Armazenamento
WL_NUMVEM = [
    ".aws/credentials", "s3-config", "k8s/", "firebase.json", 
    "storage-key.json", "client_secret.json", "service-account.json"
]
# --------------------------------------------------------------------------------
# FUNÇÕES DE INTERFACE E LOGGING
# --------------------------------------------------------------------------------
def status_log(mensagem, tipo="INFO"):
    hora = datetime.now().strftime('%H:%M:%S')
    # Mantém o print para o log do Docker, mas adiciona st.write para a Web
    texto = f"[{hora}] STATUS: {mensagem}"
    if tipo == "WARN":
        st.warning(texto)
    elif tipo == "FAIL":
        st.error(texto)
    else:
        st.write(texto)

def destacar_sessao(numero, titulo):
    # Cria uma linha visual bonita no Streamlit
    st.markdown(f"### 🔗 [ SESSÃO {numero}: {titulo} ]")

def exibir_alerta(secao, alvo, impacto_cliente, mapa_mina, ferra_ataque, extraido=None):
    # Cria um card vermelho de alerta no navegador
    with st.expander(f"🚨 FALHA DETECTADA: {secao.upper()}", expanded=True):
        st.error(f"**ALVO:** {alvo}")
        st.warning(f"**IMPACTO:** {impacto_cliente}")
        st.info(f"**MAPA DA MINA:** {mapa_mina}")
        st.code(f"ATAQUE: {ferra_ataque}")
        if extraido:
            st.success(f"DADOS: {extraido}")

# --------------------------------------------------------------------------------
# SISTEMA DE INTELIGÊNCIA ON-DEMAND (COM OPÇÃO DE PULAR)
# --------------------------------------------------------------------------------
def obter_api_shodan():
    st.markdown("### 🔑 Configuração da API Shodan")
    st.info("Insira sua chave caso queira enriquecer a auditoria com dados de inteligência de ameaças. Deixe em branco para pular.")
    
    
    chave_digitada = st.text_input(
        "Sua Shodan API Key (Opcional):",
        type="password",
        placeholder="Cole sua chave aqui ou deixe vazio para ignorar..."
    ).strip()
    
    
    return chave_digitada
def s0_inteligencia_shodan(dom):
    st.markdown("---")
    st.markdown("### 📡 Sessão 0: Inteligência Reversa (Shodan)")
    
    chave = obter_api_shodan()
    
    if not chave:
        st.warning("⏭️ **Sessão Pulada:** Nenhuma chave API do Shodan foi fornecida. Prosseguindo com os módulos locais...")
        return None
        
    try:
        import shodan
        import socket
        
        st.info(f"Conectando à API do Shodan para levantar o histórico do alvo: {dom}...")
        
        api = shodan.Shodan(chave)
        ip_alvo = socket.gethostbyname(dom)
        dados_shodan = api.host(ip_alvo)
        
        st.success(f"✅ Dados obtidos com sucesso para o IP: {ip_alvo}")
        
        with st.expander("Ver Informações de Inteligência Descobertas"):
            st.write(f"**Organização:** {dados_shodan.get('org', 'Não informada')}")
            st.write(f"**Sistema Operacional:** {dados_shodan.get('os', 'Não identificado')}")
            st.write(f"**Portas Abertas no Shodan:** {dados_shodan.get('ports', [])}")
            
    except Exception as e:
        st.error(f"❌ Erro ao processar análise: {e}")
# --------------------------------------------------------------------------------
# MOTOR DE CALIBRAGEM E ANÁLISE PROFUNDA
# --------------------------------------------------------------------------------
def calibrar_motor_llc(domain):
    """
    Sua função nativa mapeando o comportamento do alvo contra Falsos Positivos.
    """
    # Gerando um endpoint aleatório que OBRIGATORIAMENTE deve ser um 404/Inexistente
    url_falsidade = f"http://{domain}/{uuid.uuid4().hex[:12]}"
    h = {'User-Agent': random.choice(UA_LIST)}
    
    # Delay randômico (Jitter) para o scan não ser bloqueado logo na calibração
    time.sleep(random.uniform(0.5, 1.5))
    
    try:
        # Fazemos a requisição com timeout seguro e sem seguir redirects automaticamente
        r = requests.get(url_falsidade, headers=h, timeout=10, verify=False, allow_redirects=False)
        
        tamanho_base = len(r.content) if r.content else 0
        status_base = r.status_code
        server_rg = r.headers.get('Server', 'Desconhecido')
        
        # Captura uma assinatura das primeiras linhas para checar conteúdo dinâmico
        trecho_conteudo = r.text[:200].strip() if r.text else ""
        
        return {
            "ativo": True,
            "tamanho": tamanho_base,
            "status": status_base,
            "server": server_rg,
            "trecho_erro": trecho_conteudo
        }
        
    except requests.exceptions.RequestException as e:
        # Captura uma falha ao calibrar motor LLC (Alvo inacessível ou bloqueando)
        time.sleep(2)
        return {
            "ativo": False,
            "tamanho": 0,
            "status": 0,
            "server": "Desconhecido",
            "trecho_erro": ""
        }

def calcular_similaridade(html_A, html_B):
    """ Calcula a razão de semelhança entre dois textos (0.0 a 1.0) """
    if not html_A or not html_B:
        return 0.0
    return SequenceMatcher(None, html_A, html_B).ratio()

def analisador_profundo(html, assinatura_base=None):
    """
    Analisa o HTML em busca de padrões sensíveis usando expressões regulares.
    """
    # Validação inteligente: se a página atual for 95% igual à de erro, descarta (Falso Positivo)
    if assinatura_base and assinatura_base.get("ativo"):
        if calcular_similaridade(assinatura_base["trecho_erro"], html[:200].strip()) > 0.95:
            return []

    achados = []
    regex_map = {
        "CRITICAL_LFI": r"root:x:0:0",
        "CRITICAL_RCE": r"(uid=[0-9]+\(.+?\))",
        "DB_STR": r"(?:mongodb\+srv|postgres|mysql|redis)://[\w.-]+(?::\d+)?/[^\s'\"]+",
        "API_KEY": r"(?:api|secret|token|key|pass)[- ]?(?:\s*=\s*|:\s*)['\"]([a-zA-Z0-9_-]{10,45})['\"]",
        "AWS_AUTH": r"AKIA[0-9A-Z]{16}",
        "JWT_TOKEN": r"eyJ[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+\.?[A-Za-z0-9-_=]*",
        "GOOGLE_KEY": r"AIza[0-9A-Za-z_-]{35}",
        "STRIPE_KEY": r"sk_live_[0-9a-zA-Z]{24}",
        "MAILGUN_KEY": r"key-[0-9a-zA-Z]{32}",
        "TWILIO_SID": r"AC[0-9a-fA-F]{32}",
        "GH_TOKEN": r"gh[pousr][A-Za-z0-9]{36}"
    }
    
    for chave, regex in regex_map.items():
        m = re.search(regex, html, re.IGNORECASE)
        if m:
            # Guarda o tipo da falha e o trecho capturado (limitado para não estourar espaço)
            achados.append({"tipo": chave, "trecho": m.group(0)[:100]})
            
    return achados if achados else []

def triagem_vulnerabilidade_ia(dados_achados, groq_client):
    """
    Aciona a inteligência artificial na nuvem para analisar se os achados
    da Regex são reais ou falsos positivos.
    """
    try:
        # Formatamos os achados para um formato de texto limpo para o prompt
        contexto_scanner = ""
        for item in dados_achados:
            tipo_limpo = str(item.get('tipo', '')).strip()
            trecho_limpo = str(item.get('trecho', '')).strip()
            contexto_scanner += f"- Tipo: {tipo_limpo} | Trecho Capturado: {trecho_limpo}\n"
        
        # Chamada da API estruturada com prompt blindado dentro do bloco try
        response = groq_client.chat.completions.create(
            model="openai/gpt-oss-120b", # Modelo veloz ideal para triagem orientada a contexto
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Você é um perito de Red Team sênior. Avalie os achados de um scanner de vulnerabilidades automatizado. "
                        "Identifique se os trechos são vulnerabilidades reais ou falsos positivos (como códigos de exemplo, caminhos públicos normais, ou texto estático). "
                        "Se for um falso positivo, sua resposta OBRIGATORIAMENTE deve começar com a tag: [FALSO POSITIVO]. "
                        "Seja extremamente direto, responda em poucas palavras."
                    )
                },
                {
                    "role": "user",
                    "content": f"Achados brutos do motor:\n{contexto_scanner}"
                }
            ],
            temperature=0.1 # Temperatura baixa para manter a IA precisa e sem inventar dados
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"[ERRO CLOUD] Não foi possível validar via IA: {str(e)}"
def ejecutar_scan_no_endpoint(url, dados_calibragem, groq_client=None):
    """
    O CORAÇÃO DO MOTOR: Faz a requisição ao alvo, aplica as regras matemáticas
    da calibragem LLC para matar falsos positivos de infraestrutura, e valida o HTML.
    """
    h = {'User-Agent': random.choice(UA_LIST)}
    
    try:
        # ADICIONADO: Delay randômico antes de tocar no endpoint (respeito ao Rate Limiting)
        time.sleep(random.uniform(0.4, 1.2))
        
        # Executa o teste na URL de auditoria real
        r = requests.get(url, headers=h, timeout=10, verify=False, allow_redirects=False)
        
        # --- FILTRO 1: COMPARAÇÃO DINÂMICA (Anti-Wildcard / Páginas Falsas) ---
        # Se o site retorna o mesmo status e tamanho da página de erro capturada na calibragem, descarte.
        if r.status_code == dados_calibragem["status"] and len(r.content) == dados_calibragem["tamanho"]:
            return None
            
        # Checagem de tolerância por conteúdo dinâmico (ex: páginas com relógio que mudam poucos bytes)
        trecho_atual = r.text[:200].strip() if r.text else ""
        if trecho_atual == dados_calibragem["trecho_erro"] and dados_calibragem["trecho_erro"] != "":
            return None
            
        # --- FILTRO 2: ANALISADOR NATIVO (REGEX) ---
        # Se passou pela calibragem, o endpoint respondeu algo diferente do padrão de erro. Vamos escanear o HTML.
        achados_regex = analisador_profundo(r.text)
        
        if achados_regex:
            # --- FILTRO 3: SEGUNDO FATOR COGNITIVO (IA NA NUVEM) ---
            # Se a Regex encontrou algo suspeito e temos a IA configurada, enviamos para triagem de elite
            if groq_client:
                resultado_triagem = triagem_vulnerabilidade_ia(achados_regex, groq_client)
                
                # Se a IA bater o martelo que é um falso positivo, o motor descarta e não polui o log
                if "[FALSO POSITIVO]" in resultado_triagem:
                    return None
                
                # Retorna o achado validado pela inteligência artificial
                return {
                    "url": url,
                    "status_code": r.status_code,
                    "achados": achados_regex,
                    "validacao_ia": resultado_triagem
                }
            else:
                # Se não houver IA ativa, retorna o achado bruto da regex normalmente
                return {
                    "url": url,
                    "status_code": r.status_code,
                    "achados": achados_regex,
                    "validacao_ia": "IA não acionada (Triagem Cloud desativada)"
                }
                
        return None
        
    except requests.exceptions.RequestException:
        # Se o endpoint falhar ou cair durante o scan, o motor absorve o erro e continua
        return None
def rodar_varredura_multi_threading(domain, lista_caminhos, dados_calibragem, groq_client):
    """
    Orquestra a execução paralela usando a sua função 'executar_scan_no_endpoint'.
    Lê a wordlist de diretórios e gerencia as threads no Streamlit.
    """
    resultados_validos = []
    
    # Constrói a lista completa de alvos para passar para o motor
    urls_para_testar = [f"http://{domain}/{caminho.lstrip('/')}" for caminho in lista_caminhos]
    
    # Elementos visuais dinâmicos para o painel do Streamlit
    barra_progresso = st.progress(0)
    status_texto = st.empty()
    container_alerts = st.container()
    
    total_testes = len(urls_para_testar)
    
    if total_testes == 0:
        st.warning("⚠️ Nenhum caminho foi carregado para teste.")
        return resultados_validos
        
    # Abre o pool usando as estruturas que você importou no topo
    with ThreadPoolExecutor(max_workers=15) as executor:
        # Mapeia cada thread apontando diretamente para o seu motor atual
        futuros = {
            executor.submit(ejecutar_scan_no_endpoint, url, dados_calibragem, groq_client): url
            for url in urls_para_testar
        }
        
        concluidos = 0
        for futuro in as_completed(futuros):
            concluidos += 1
            url_atual = futuros[futuro]
            
            # Atualização de status em tempo real na interface web
            status_texto.markdown(f"**⚡ Progresso do Motor:** `[{concluidos}/{total_testes}]` escaneando {url_atual}")
            barra_progresso.progress(concluidos / total_testes)
            
            try:
                # Resgata o retorno da requisição de forma segura
                resultado = futuro.result()
                
                # Correção: Valida se o retorno é um dicionário antes de extrair as chaves
                if resultado is not None:
                    resultados_validos.append(resultado)
                    
                    # Se o seu motor detectou algo real e a IA validou, joga na tela
                    with container_alerts:
                        st.error(f"🚨 **Falha Confirmada:** {resultado['url']} | Status: {resultado['status_code']}")
                        st.json(resultado['achados'])
                        
            except Exception as e:
                # Registra erros internos das threads de forma segura no terminal do Kali
                print(f"[Erro Interno Thread] {url_atual}: {str(e)}")
                
    # Finalização do painel visual após o fechamento do pool de threads
    status_texto.success(f"▀▄ *Auditoria Industrial Concluída!* `{len(resultados_validos)}` vulnerabilidades reais isoladas.")
    return resultados_validos
# SESSÕES OPERACIONAIS DE AUDITORIA
# --------------------------------------------------------------------------------

def s1_recon_dns(dom):
    destacar_sessao("1", "RECONHECIMENTO DNS AVANÇADO (NATIVO)")
    status_log(f"Iniciando resolução e mapeamento de infraestrutura para: {dom}", "INFO")
    
    # Sanitização precisa para isolar o Host/IP limpo do alvo
    alvo_limpo = dom.replace("https://", "").replace("http://", "").split('/')[0].strip()
    
    # 1. Resolução do IP Principal do Alvo
    try:
        ip_base = socket.gethostbyname(alvo_limpo)
        status_log(f"Alvo resolvido com sucesso! IP Principal: {ip_base}", "OK")
    except socket.gaierror:
        status_log("Falha crítica na resolução do Host. Verifique o domínio.", "FAIL")
        st.error(f"❌ Não foi possível resolver o domínio principal: {alvo_limpo}")
        return

    # 2. Mapeamento Multithreading de Serviços Adjacentes Comuns
    subdominios_criticos = ["www", "mail", "ftp", "admin", "webmail", "ns1", "api"]
    ips_descobertos = {}
    
    # Função interna de checagem executada de forma assíncrona pelas threads
    def checar_subdominio(sub):
        host_teste = f"{sub}.{alvo_limpo}"
        try:
            ip_resolvido = socket.gethostbyname(host_teste)
            return sub, ip_resolvido
        except socket.gaierror:
            return sub, None

    # Motor Concorrente: usa o ThreadPoolExecutor já importado do seu ambiente
    with ThreadPoolExecutor(max_workers=5) as executor:
        futuros = {executor.submit(checar_subdominio, sub): sub for sub in subdominios_criticos}
        
        for futuro in as_completed(futuros):
            sub, ip_resultado = futuro.result()
            if ip_resultado:
                ips_descobertos[sub] = ip_resultado

    # --- RELATÓRIO INTERFACE GRÁFICA (STREAMLIT) ---
    st.write("### 🔍 Painel de Inteligência e Resolução DNS")
    
    # Exibição de Indicadores de Destaque (Metrics)
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Endereço IPv4 Principal", value=ip_base)
    with col2:
        st.metric(label="Hosts Adicionais Encontrados", value=len(ips_descobertos))

    # Divisão por abas para organizar as informações de segurança do alvo
    aba_principal, aba_infraestrutura = st.tabs([
        "📌 Alvo Principal", 
        "🌐 Infraestrutura Adjacente (Subdomínios Ativos)"
    ])

    with aba_principal:
        st.markdown(f"*Dados de conexão direta para o domínio consultado:*")
        st.info(f"O domínio *{alvo_limpo}* aponta diretamente para o servidor de hospedagem no endereço IP *{ip_base}*.")
        
        st.table({
            "Propriedade": ["Host Consultado", "IP Retornado", "Status de Resolução"], 
            "Valor": [alvo_limpo, ip_base, "Ativo / Respondendo"]
        })

    with aba_infraestrutura:
        if ips_descobertos:
            st.markdown("*Hosts e serviços associados ativos mapeados via varredura de sockets:*")
            
            tabela_dados = {
                "Serviço / Subdomínio": [f"{k}.{alvo_limpo}" for k in ips_descobertos.keys()],
                "Endereço IP Associado": list(ips_descobertos.values())
            }
            st.dataframe(tabela_dados, use_container_width=True)
        else:
            st.warning("Nenhum subdomínio padrão adicional respondeu aos testes de socket na mesma faixa de DNS.")
def s2_geo_infra(dom):
    st.markdown("### 🌐 Sessão 2: Mapeamento de Infraestrutura e Geo-IP")
    
    with st.spinner("Resolvendo DNS e buscando dados de geolocalização..."):
        try:
            ip_address = socket.gethostbyname(dom)
            st.success(f"*Alvo resolvido com sucesso:* {ip_address}")
        except Exception as e:
            st.error(f"❌ Falha crítica na resolução de DNS para o domínio {dom}: {e}")
            return None

        try:
            url = f"http://ip-api.com/json/{ip_address}"
            response = requests.get(url, timeout=5).json()
            
            if response.get("status") == "success":
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        label="📍 Localização", 
                        value=f"{response.get('city', 'N/D')}", 
                        delta=response.get('countryCode', '')
                    )
                
                with col2:
                    isp = response.get('isp', 'N/D')
                    st.metric(
                        label="🏢 Provedor (ISP)", 
                        value=f"{isp[:15]}..." if len(isp) > 15 else isp
                    )
                    
                with col3:
                    st.metric(
                        label="🔀 ASN", 
                        value=f"{response.get('as', 'N/D').split()[0]}"
                    )
                
                with st.expander("Ver dados brutos de Geolocalização"):
                    st.json(response)
                    
                return ip_address
            else:
                st.warning("⚠️ API de Geo-IP retornou status de falha.")
                return ip_address
                
        except Exception as e:
            st.warning(f"⚠️ Dados de geolocalização indisponíveis: {e}")
            return ip_address
def s3_fingerprint_tecnologico(dom):
    """
    SESSÃO 3: Fingerprint Tecnológico & Banner Grabbing.
    Identifica de forma precisa servidores, tecnologias de borda, WAF e CDN.
    """
    st.markdown("### 🔍 Sessão 3: Fingerprint e Banner Grabbing")
    st.info("Interrogando cabeçalhos HTTP para identificar WAF, CDN e Infraestrutura...")
    
    # Seleção aleatória de User-Agent usando a lista global do topo do arquivo
    headers = {'User-Agent': random.choice(UA_LIST)}
    
    try:
        # Sanitização rápida da URL para evitar quebras no requests
        url_alvo = f"http://{dom}" if not dom.startswith(("http://", "https://")) else dom
        
        # Requisição de auditoria com timeout curto e SSL flexível
        r = requests.get(url_alvo, timeout=5, verify=False, headers=headers)
        
        server = r.headers.get('Server', 'Não detectado')
        pow_by = r.headers.get('X-Powered-By', 'Não detectado')
        
        # --- EXIBIÇÃO DOS BANNERS DO SERVIDOR ---
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="🖥️ Servidor (Banner)", value=server)
        with col2:
            st.metric(label="⚙️ Tecnologia Base", value=pow_by)
            
        # --- DETECÇÃO DE WAF / PROTEÇÕES ---
        waf_hits = []
        headers_str = "".join(r.headers.keys()).lower()
        
        # Varredura de assinaturas de cabeçalho (Mapeamento Industrial)
        if any(h in headers_str for h in ["x-vercel-id", "x-vercel-cache"]):
            waf_hits.append("Vercel Edge")
        if "cf-ray" in r.headers:
            waf_hits.append("Cloudflare WAF / CDN")
        if "x-akamai-transformed" in r.headers:
            waf_hits.append("Akamai WAF")
        if "x-amz-id-2" in r.headers:
            waf_hits.append("AWS S3 / CloudFront")
            
        # --- PAINEL DE ANÁLISE DE BORDA ---
        st.markdown("#### 🛡️ Análise de Proteção de Borda (WAF/CDN)")
        if waf_hits:
            for waf in waf_hits:
                st.warning(f"⚠️ WAF/INFRA DETECTADA: {waf}")
        else:
            st.success("🟢 PROTEÇÃO WAF: Nenhuma assinatura óbvia de WAF/CDN foi identificada nos cabeçalhos padrão.")
            
        # --- EXPANDER COM OS CABEÇALHOS COMPLETOS ---
        with st.expander("📂 Ver todos os cabeçalhos HTTP brutos (Headers)"):
            st.json(dict(r.headers))
            
        # Retorna o dicionário populado para o estado do painel (v37.0)
        return {
            "servidor": server,
            "tecnologia": pow_by,
            "protecoes": waf_hits if waf_hits else ["Nenhuma detectada"]
        }
        
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Erro ao conectar no alvo para Fingerprint: {e}")
        return None
def s4_owasp_headers(dom):
    st.markdown("### 🛡️ Sessão 4: Cabeçalhos de Segurança (OWASP Top 10)")
    st.info("Validando políticas contra Injeção, XSS, Clickjacking e HSTS...")

    UA_LIST = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ]
    headers = {'User-Agent': random.choice(UA_LIST)}

    try:
        r = requests.get(f"http://{dom}", timeout=5, verify=False, headers=headers)
        
        headers_map = {
            "Content-Security-Policy": "Risco de Cross-Site Scripting (XSS) e injeções de script.",
            "X-Frame-Options": "Permite ataques de Clickjacking (o site pode ser embutido em iframes maliciosos).",
            "X-Content-Type-Options": "MIME Sniffing ativado (o navegador pode executar arquivos com formatos estritos).",
            "Strict-Transport-Security": "HSTS não configurado (tráfego HTTP não é forçado para HTTPS de forma segura).",
            "Referrer-Policy": "Referrer-Policy não configurado (pode vazar dados de navegação para links externos).",
            "Permissions-Policy": "Permissions-Policy não configurado (recursos como câmera/microfone não estão restritos)."
        }

        # Listas para organizar o resultado visualmente
        ativos = []
        ausentes = []

        for h, risco in headers_map.items():
            # Verifica a existência do cabeçalho de forma case-insensitive
            match = next((k for k in r.headers if k.lower() == h.lower()), None)
            
            if match:
                ativos.append((h, r.headers[match]))
            else:
                ausentes.append((h, risco))

        # Exibição dos resultados em colunas para melhorar o design
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### ✅ Proteções Ativas")
            if ativos:
                for h, valor in ativos:
                    st.success(f"*{h}*: Ativo")
            else:
                st.write("Nenhum cabeçalho recomendado foi detectado.")

        with col2:
            st.markdown("#### ❌ Vulnerabilidades / Ausências")
            if ausentes:
                for h, risco in ausentes:
                    st.error(f"*{h}\n\n*Risco: {risco}")
            else:
                st.success("Excelente! Todos os cabeçalhos OWASP validados estão configurados.")

    except Exception as e:
        st.error(f"❌ Erro ao validar cabeçalhos OWASP no alvo: {e}")
# MOTOR DE FUZZING PARALELO INDUSTRIAL (PADRÃO ELITE)
# =====================================================================

def core_fuzzing_worker(url, cal, secao, timeout_global=15):
    """
    Trabalhador focado em fazer a requisição de forma limpa e isolada,
    evitando poluição de variáveis globais.
    """
    fake_ip = f"{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}"
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        'X-Forwarded-For': fake_ip,
        'Client-IP': fake_ip
    }
    
    try:
        r = requests.get(url, headers=headers, timeout=timeout_global, verify=False, allow_redirects=False)
        
        if r.status_code in [301, 302, 307, 308, 404]:
            return None
            
        if r.status_code == 200:
            t_atual = len(r.content) if r.content else 0
            tamanho_base = cal.get("tamanho", 0)
            
            # Margem dinâmica calibrada (15% de variação tolerada)
            margem_waf = tamanho_base * 0.15
            
            if t_atual < 100 or abs(t_atual - tamanho_base) <= margem_waf:
                return None
                
            # Dispara análise de assinaturas locais se a função existir
            segredos = analisador_profundo(r.text) if 'analisador_profundo' in globals() else []
            
            return {
                "secao": secao,
                "url": url,
                "status_code": r.status_code,
                "tipo": "Vazamento Estrutural" if segredos else "Diretório/Arquivo Real Exposto",
                "detalhe": f"Tamanho: {t_atual} bytes | {len(segredos)} assinaturas detectadas.",
                "segredos": ", ".join(segredos) if segredos else "Nenhum"
            }
            
    except requests.exceptions.RequestException:
        pass
    return None


def s5_6_7_multi_fuzz(dom, cal, threads_motor=10):
    """
    Orquestrador otimizado: Processa em lote para não congelar o Streamlit
    e monta a lista de tarefas usando o session_state isolado por usuário.
    """
    st.markdown("### 🛠️ Motor de Fuzzing Paralelo Industrial")

    # Puxa os dados com segurança do session_state do usuário atual
    w_dir = st.session_state.wordlist_diretorios
    w_api = st.session_state.wordlist_api
    w_nuv = st.session_state.wordlist_nuvem

    full_list = []
    for p in w_dir: full_list.append((p, "DIRETÓRIO"))
    for p in w_api: full_list.append((p, "API"))
    for p in w_nuv: full_list.append((p, "CLOUD"))

    if not full_list:
        st.warning("⚠️ Nenhuma wordlist válida foi fornecida ou carregada.")
        return []

    st.info(f"🚀 Iniciando varredura híbrida com {threads_motor} threads sobre {len(full_list)} caminhos...")

    resultados_fuzzing = []

    # COMPONENTES VISUAIS FIXOS
    barra_progresso = st.progress(0.0)
    status_texto = st.empty()
    tabela_placeholder = st.empty() 

    total_tarefas = len(full_list)

    with ThreadPoolExecutor(max_workers=threads_motor) as ex:
        futuros = {
            ex.submit(core_fuzzing_worker, f"http://{dom}/{path.lstrip('/')}", cal, tipo): (path, tipo)
            for path, tipo in full_list
        }

        for i, futuro in enumerate(as_completed(futuros)):
            try:
                resultado = futuro.result()
                if resultado:
                    resultados_fuzzing.append(resultado)
                    tabela_placeholder.dataframe(resultados_fuzzing, use_container_width=True)
            except Exception:
                pass

            # CORREÇÃO 1: Usar uma variável estável para não quebrar o layout do scroll
            percentual = (i + 1) / total_tarefas
            barra_progresso.progress(percentual)
            status_texto.markdown(f"`[{i + 1}/{total_tarefas}]` caminhos verificados...")

    # CORREÇÃO 2: NUNCA use .empty() aqui. 
    # Mantemos o elemento vivo com uma mensagem de sucesso para travar a altura da página.
    barra_progresso.progress(1.0)
    status_texto.markdown("✨ **Varredura encerrada no motor híbrido.**")

    if resultados_fuzzing:
        st.error(f"🚨 Fuzzing Finalizado: Foram encontrados {len(resultados_fuzzing)} caminhos reais expostos!")
    else:
        st.success("✅ Fuzzing Finalizado: Nenhum diretório sensível exposto foi detectado.")

    return resultados_fuzzing
def s8_port_scanner(dom):
    st.markdown("### 🔌 Sessão 8: Varredura de Portas Operacionais")
    st.info("Testando portas e serviços mais comuns no alvo para identificar vetores de exposição...")
    
    # Lista de portas padrão do seu script original
    portas = [21, 22, 23, 25, 53, 80, 110, 143, 443, 465, 587, 993, 995, 3306, 3389, 5432, 5900, 6379, 8080]
    
    # Mapeamento profissional de serviços comuns para enriquecer a tabela
    servicos_map = {
        21: "FTP (Transferência de Arquivos)", 22: "SSH (Acesso Remoto Seguro)", 
        23: "Telnet (Inseguro)", 25: "SMTP (E-mail)", 53: "DNS", 
        80: "HTTP (Web)", 110: "POP3 (E-mail)", 143: "IMAP (E-mail)", 
        443: "HTTPS (Web Seguro)", 465: "SMTPS", 587: "SMTP Submission", 
        993: "IMAPS", 995: "POP3S", 3306: "MySQL (Banco de Dados)", 
        3389: "RDP (Área de Trabalho Remota)", 5432: "PostgreSQL", 
        5900: "VNC", 6379: "Redis (Cache)", 8080: "HTTP Alternativo"
    }
    
    portas_abertas = []
    
    # Componentes dinâmicos de carregamento na interface web
    progresso = st.progress(0.0)
    status_texto = st.empty()
    tabela_placeholder = st.empty()
    
    total_portas = len(portas)
    
    for i, p in enumerate(portas):
        status_texto.text(f"Escaneando porta {p} ({servicos_map.get(p, 'Desconhecido')})...")
        
        try:
            # Cria o socket com timeout curto para manter a alta disponibilidade na web
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.6)  # Padrão rápido e estável
            
            # Executa a tentativa de conexão
            resultado = s.connect_ex((dom, p))
            
            if resultado == 0:
                # Porta aberta encontrada! Adiciona na lista estruturada
                portas_abertas.append({
                    "Porta": f"🟢 {p}",
                    "Serviço Esperado": servicos_map.get(p, "Desconhecido"),
                    "Status": "Aberta / Exposta",
                    "Vetor": "Alvo em potencial para Brute-Force / Enumeração" if p in [22, 23, 3389, 3306] else "Serviço Ativo"
                })
                # Atualiza a tabela na tela em tempo real
                tabela_placeholder.dataframe(portas_abertas, use_container_width=True)
                
            s.close()
        except Exception:
            pass
            
        # Atualiza a barra de progresso sem dar engasgos na tela
        progresso.progress((i + 1) / total_portas)
        
    # Limpa os componentes temporários após a execução
    status_texto.empty()
    progresso.empty()
    
    # Retorno final na interface
    if portas_abertas:
        st.error(f"🚨 *Varredura Concluída:* Foram encontradas {len(portas_abertas)} portas abertas expostas na internet!")
    else:
        st.success("✅ *Varredura Concluída:* Nenhuma das principais portas operacionais testadas está exposta diretamente.")
        
    return portas_abertas
def s9_cookies_session(dom):
    st.markdown("---")
    st.markdown("### 🍪 Sessão 9: Análise de Cookies e Segurança de Sessão")
    st.info("Interrogando a aplicação para analisar as políticas de proteção dos cookies de sessão...")
    
    try:
        import requests
        import random
        
        # Lista de User-Agents padrão para evitar bloqueios simples
        UA_LIST = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]
        headers = {'User-Agent': random.choice(UA_LIST)}
        
        # Faz a requisição testando HTTP e tratando redirecionamentos de forma segura
        r = requests.get(f"http://{dom}", timeout=5, verify=False, headers=headers, allow_redirects=True)
        
        if r.cookies:
            st.warning(f"🚨 **{len(r.cookies)} cookie(s)** foram detectados na sessão. Analisando conformidade com as diretrizes OWASP:")
            
            analise_cookies = []
            
            for c in r.cookies:
                # Avalia o estado de cada flag de segurança
                is_secure = "🟢 SIM" if c.secure else "🔴 NÃO (Vulnerável)"
                
                # HttpOnly e SameSite exigem checagem de atributos internos ou dicionário do cookie
                is_httponly = "🟢 SIM" if c.has_nonstandard_attr('HttpOnly') or 'httponly' in [k.lower() for k in c.__dict__.keys()] else "🔴 NÃO (Vulnerável)"
                
                samesite_attr = c.get_nonstandard_attr('SameSite') if c.has_nonstandard_attr('SameSite') else "Não definido"
                is_samesite = f"🟢 {samesite_attr}" if samesite_attr in ["Lax", "Strict"] else "🟡 Não configurado"
                
                # Monta a estrutura de dados para o componente visual do Streamlit
                analise_cookies.append({
                    "Nome do Cookie": c.name,
                    "Valor (Truncado)": c.value[:15] + "..." if len(c.value) > 15 else c.value,
                    "Secure (HTTPS)": is_secure,
                    "HttpOnly (Anti-XSS)": is_httponly,
                    "SameSite (Anti-CSRF)": is_samesite
                })
            
            # Renderiza os resultados em um DataFrame responsivo e limpo
            st.dataframe(analise_cookies, use_container_width=True)
            
            # Adiciona alertas contextuais se houver falhas críticas
            for cookie in analise_cookies:
                if "🔴" in cookie["HttpOnly (Anti-XSS)"]:
                    st.error(f"⚠️ **Risco Crítico:** O cookie `{cookie['Nome do Cookie']}` não possui a flag **HttpOnly**. Se o alvo sofrer um ataque de XSS, o token de sessão poderá ser roubado via JavaScript (`document.cookie`).")
                if "🔴" in cookie["Secure (HTTPS)"]:
                    st.error(f"⚠️ **Risco:** O cookie `{cookie['Nome do Cookie']}` não possui a flag **Secure**. Ele pode ser interceptado se trafegar em redes Wi-Fi públicas ou conexões HTTP puras.")
                    
        else:
            st.success("✅ **Varredura de Cookies Concluída:** Nenhum cookie foi injetado na resposta inicial do cabeçalho. (Aplicação stateless ou cookies gerados via JS dinâmico).")
            
   
    except Exception as e:
        st.error(f"❌ Erro ao realizar análise de cookies e sessão no alvo: {e}")

# =====================================================================
# === SESSÃO 10: FINALIZAÇÃO E RELATÓRIO EXECUTIVO DA IA (COMPLETO) ===
def s10_log_final(alvo, log_completo, relatorio):
    # 1. Spinner para indicar processamento
    with st.spinner("🤖 IA processando dados..."):
        dados = analisar_logs_via_nuvem(log_completo, alvo)

    # 2. DEBUG: Se isto não aparecer na tela, a função está retornando vazio ou erro
    if not dados:
        st.error("ERRO: A função de nuvem retornou um dicionário vazio ou None.")
        return
    
    # Exibe o dicionário bruto para você ter certeza do que a IA está mandando
    with st.expander("🔍 Ver dados brutos (Debug)"):
        st.write(dados)

    # 3. RENDERIZAÇÃO DOS DADOS (Agora que sabemos que 'dados' é um dict)
    st.markdown("---")
    st.subheader("📊 Relatório de Auditoria")
    
    # Acessando as chaves que você definiu na sua nuvem
    # Ajuste os nomes das chaves conforme o que aparecer no DEBUG acima
    st.metric("Alvo Identificado", dados.get("alvo", "Não informado"))
    
    st.markdown("### 📝 Análise Técnica")
    st.info(dados.get("resumo_executivo", "Sem resumo disponível."))
    
    st.markdown("### ⚠️ Nível de Risco")
    st.warning(dados.get("nivel_risco_geral", "Sem classificação."))

    st.success("Fim do relatório.")
# --------------------------------------------------------------------------------
# SESSÕES DE PÓS-EXPLORAÇÃO E AUXILIARES
# --------------------------------------------------------------------------------

def s11_identificador_hash(dom):
    destacar_sessao("11", "PESQUISADOR E IDENTIFICADOR DE HASH AVANÇADO (PRO ENGINE)")
    st.info("🧬 Analisando assinaturas criptográficas e mapeando vetores de quebra tática...")
    
    # Campo de texto interativo na tela do navegador
    hash_input = st.text_input(
        "🔑 Insira a assinatura (Hash) para análise:", 
        placeholder="Ex: 8743b52063cd84097a65d1633...", 
        key="hash_s11"
    ).strip()
    
    if hash_input:
        # Remove espaços ou quebras de linha acidentais
        hash_clean = re.sub(r'\s+', '', hash_input)
        tamanho = len(hash_clean)
        is_hex = all(c in "0123456789abcdefABCDEF" for c in hash_clean)
        
        # --- PAINEL DE METADADOS ULTRA ORGANIZADO ---
        col_t, col_c = st.columns(2)
        with col_t:
            st.metric(label="Comprimento do Hash", value=f"{tamanho} caracteres")
        with col_c:
            st.metric(label="Composição Detectada", value="Hexadecimal" if is_hex else "Complexa / Especial")
            
        formatos_detectados = []
        hashcat_mode = ""
        john_format = ""
        complexidade = "Média"
        cor_alert = "🟡"

        # --- CAMADA 1: IDENTIFICAÇÃO POR REGEX EXPANDIDO ---
        # MD5
        if tamanho == 32 and re.match(r"^[a-fA-F0-9]{32}$", hash_clean):
            formatos_detectados.append("MD5")
            hashcat_mode = "-m 0"
            john_format = "--format=raw-md5"
            complexidade = "Baixa (Suscetível a tabelas Rainbow e colisões rápidas)"
            cor_alert = "🟢"
        # NTLM (Windows)
        elif tamanho == 32 and is_hex:
            # Mantém como fallback pois NTLM também tem 32 hex chars
            formatos_detectados.append("NTLM (Windows LM/NT)")
            hashcat_mode = "-m 1000"
            john_format = "--format=nt"
            complexidade = "Baixa (Velocidade de quebra extremamente alta via GPU)"
            cor_alert = "🟢"
        # SHA-1
        elif tamanho == 40 and re.match(r"^[a-fA-F0-9]{40}$", hash_clean):
            formatos_detectados.append("SHA-1")
            hashcat_mode = "-m 100"
            john_format = "--format=raw-sha1"
            complexidade = "Baixa (Algoritmo legado, quebra rápida)"
            cor_alert = "🟢"
        # SHA-256
        elif tamanho == 64 and re.match(r"^[a-fA-F0-9]{64}$", hash_clean):
            formatos_detectados.append("SHA-256")
            hashcat_mode = "-m 1400"
            john_format = "--format=raw-sha256"
            complexidade = "Média (Exige bom dicionário ou hardware dedicado)"
            cor_alert = "🟡"
        # SHA-512
        elif tamanho == 128 and re.match(r"^[a-fA-F0-9]{128}$", hash_clean):
            formatos_detectados.append("SHA-512")
            hashcat_mode = "-m 1700"
            john_format = "--format=raw-sha512"
            complexidade = "Alta (Robusto, exige alto processamento)"
            cor_alert = "🔴"
        # BCrypt
        elif hash_clean.startswith("$2a$") or hash_clean.startswith("$2b$") or hash_clean.startswith("$2y$"):
            if tamanho == 60:
                formatos_detectados.append("Bcrypt (Blowfish Extension)")
                hashcat_mode = "-m 3200"
                john_format = "--format=bf"
                complexidade = "Extremamente Alta (Usa Key Stretching / Salt nativo. Muito lento para brute-force)"
                cor_alert = "🔴"

        # --- CAMADA 2: MOTOR EXTERNA HASHID (ENRIQUECIMENTO DE BACKUP) ---
        try:
            import hashid
            hd = hashid.HashID()
            identificacoes_ext = list(hd.identifyHash(hash_clean))
            for i in identificacoes_ext:
                if i.name not in formatos_detectados:
                    formatos_detectados.append(i.name)
        except Exception:
            pass

        # --- INTERFACE DE EXIBIÇÃO AVANÇADA ---
        if formatos_detectados:
            st.success(f"🎯 *Candidato(s) Detectado(s):* {', '.join(formatos_detectados)}")
            st.info(f"{cor_alert} *Complexidade de Quebra:* {complexidade}")
            
            # Exibe o Card Estratégico se houver comandos mapeados
            if hashcat_mode or john_format:
                with st.expander("🚀 Playbook do Auditor (Comandos Ofensivos de Cracking)", expanded=True):
                    st.markdown("Execute os comandos estruturados abaixo no terminal do seu laboratório:")
                    
                    if hashcat_mode:
                        st.markdown("*Ataque via Hashcat (Otimizado para GPU):*")
                        st.code(f"hashcat {hashcat_mode} hash_alvo.txt wordlist.txt", language="bash")
                    if john_format:
                        st.markdown("*Ataque via John the Ripper (Otimizado para CPU):*")
                        st.code(f"john {john_format} --wordlist=wordlist.txt hash_alvo.txt", language="bash")
                    
                    st.caption("📂 Dica industrial: Salve a assinatura limpa em um arquivo chamado hash_alvo.txt antes de disparar os motores.")
        else:
            st.warning("⚠️ O motor avançado não encontrou uma assinatura comercial óbvia. Tente checar se há caracteres residuais ou salts embutidos.")
            
    else:
        st.info("ℹ️ Insira um hash no campo acima para acionar o motor de análise multi-camadas e os playbooks de quebra.")
def s12_privilege_escalation_auditor(url_alvo):
    st.write("### 🛡️ AUDITOR DE PORTAS ADMINISTRATIVAS & BANNER GRABBING")
    
    # Limpeza da URL (Mantendo a sua lógica original)
    alvo = url_alvo.replace("https://", "").replace("http://", "").split('/')[0]
    
    portas_criticas = {
        22: "SSH/Acesso Remoto",
        80: "HTTP (Web)",
        443: "HTTPS (Secure Web)",
        3306: "MySQL Database",
        3389: "RDP (Windows Remote Desktop)",
        8080: "HTTP Alternativo / Tomcat",
        8443: "HTTPS Alternativo"
     }

    for porta, servico in portas_criticas.items():
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2.5)
            resultado = sock.connect_ex((alvo, porta))
            
            if resultado == 0:
                banner = ""
                # Tratamento para portas SSL/TLS
                if porta in [443, 8443]:
                    try:
                        contexto = ssl.create_default_context()
                        contexto.check_hostname = False
                        contexto.verify_mode = ssl.CERT_NONE
                        sock_ssl = contexto.wrap_socket(sock, server_hostname=alvo)
                        requisicao = f"HEAD / HTTP/1.1\r\nHost: {alvo}\r\nConnection: close\r\n\r\n"
                        sock_ssl.sendall(requisicao.encode('utf-8'))
                        resposta = sock_ssl.recv(2048).decode(errors='ignore')
                        
                        for linha in resposta.split("\r\n"):
                            if "Server:" in linha or "X-Powered-By:" in linha:
                                banner += f"[{linha.strip()}] "
                        if not banner:
                            banner = resposta.split("\r\n")[0]
                    except:
                        banner = "Conexão SSL estabelecida, mas sem banner HTTP claro."
                
                # Tratamento para portas HTTP comuns
                elif porta in [80, 8080]:
                    requisicao = f"HEAD / HTTP/1.1\r\nHost: {alvo}\r\nConnection: close\r\n\r\n"
                    sock.sendall(requisicao.encode('utf-8'))
                    resposta = sock.recv(2048).decode(errors='ignore')
                    for linha in resposta.split("\r\n"):
                        if "Server:" in linha or "X-Powered-By:" in linha:
                            banner += f"[{linha.strip()}] "
                    if not banner:
                        banner = resposta.split("\r\n")[0]
                
                # Serviços Raw (SSH, RDP, MySQL)
                else:
                    sock.send(b"\r\n")
                    resposta = sock.recv(1024).decode(errors='ignore').strip()
                    banner = resposta.replace('\n', ' ').replace('\r', '')[:60] if resposta else "Sem banner para serviço Raw"

                st.success(f"Porta {porta} ({servico}) encontrada!")
                st.info(f"*Banner:* {banner}")
            
                sock.close()
        except Exception as e:
            st.error(f"Erro na porta {porta}: {e}")
def s13_bruteforce_simulation(dom):
    destacar_sessao("13", "SIMULAÇÃO DE BRUTE-FORCE (AUTH)")
    status_log("Testando vulnerabilidade a brute-force em endpoints comuns...", "INFO")
    
    # Sua lista original expandida com caminhos modernos de API
    endpoints = [
        "/login", "/admin/login", "/wp-login.php", "/api/auth/login", 
        "/admin", "/administrator", "/console", "/dashboard"
    ]
    
    # Elementos dinâmicos do Streamlit para acompanhar a velocidade das Threads
    barra_progresso = st.progress(0)
    status_dinamico = st.empty()
    total_eps = len(endpoints)
    
    # Função que será executada em paralelo pelas Threads
    def verificar_url(ep):
        url = f"http://{dom.strip()}{ep}"
        try:
            r = requests.get(url, timeout=5, verify=False)
            if r.status_code == 200:
                return {"url": url, "ep": ep, "status": 200}
        except requests.RequestException:
            pass
        return None

    # Executa até 4 requisições simultâneas (muito mais rápido)
    with ThreadPoolExecutor(max_workers=4) as executor:
        futuros = {executor.submit(verificar_url, ep): ep for ep in endpoints}
        
        for index, futuro in enumerate(as_completed(futuros)):
            resultado = futuro.result()
            if resultado:
                # Dispara o seu alerta customizado nativo do seu framework
                exibir_alerta("Sessão 13", resultado["url"], "Risco de Brute-force.", f"Endpoint de login exposto: {resultado['ep']}", "Hydra / Medusa")
            
            # Atualiza a barra de progresso do Streamlit em tempo real
            barra_progresso.progress((index + 1) / total_eps)
            
    # Limpa os indicadores de progresso ao finalizar
    barra_progresso.empty()
def s14_mysql_root_audit(url_alvo):
    # Cabeçalho da sessão
    st.markdown("---")
    st.subheader("🔍 AUDITORIA DE CREDENCIAIS ROOT (DATABASE)")
    
    # Limpeza da URL
    alvo = url_alvo.replace("https://", "").replace("http://", "").split('/')[0]
    
    # Placeholder para log de status no Streamlit
    status_placeholder = st.empty()
    status_placeholder.info(f"Analisando comportamento do serviço MySQL/MariaDB em {alvo}:3306...")

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(4.0)
            resultado = sock.connect_ex((alvo, 3306))

            if resultado == 0:
                # Captura de banner (handshake inicial)
                packet = sock.recv(1024)
                
                if packet and len(packet) > 5:
                    # Verifica se o protocolo é MySQL baseado nos bytes iniciais
                    is_mysql = b"mysql" in packet.lower() or b"mariadb" in packet.lower() or packet[4] == 10
                    
                    if is_mysql:
                        # Extração limpa do banner
                        banner_limpo = "".join([chr(b) for b in packet if 32 <= b < 127]).strip()
                        
                        # Definição de exibição conforme o conteúdo
                        if "mysql" in banner_limpo.lower():
                            banner_exibicao = "MySQL Server (Handshake Ativo)"
                        elif "mariadb" in banner_limpo.lower():
                            banner_exibicao = "MariaDB Server (Handshake Ativo)"
                        else:
                            banner_exibicao = "Serviço compatível com MySQL Protocol"
                        
                        status_placeholder.success("Porta 3306 ativa e respondendo ao protocolo de BD.")
                        
                        # Disparo do alerta visual (usando sua função ou st.error para alto impacto)
                        exibir_alerta(
                            "Sessão 14",
                            f"{alvo}:3306",
                            "Acesso Total / Exposição Crítica.",
                            f"Instância exposta publicamente: {banner_exibicao}. Risco severo de força bruta ou exploit direto. Comando: mysql -h {alvo} -u root"
                        )
                    else:
                        status_placeholder.warning("Porta 3306 aberta, mas o payload não corresponde ao protocolo MySQL.")
                else:
                    status_placeholder.warning("Porta 3306 aberta, mas não houve envio de banner de boas-vindas.")
            else:
                status_placeholder.error("Porta 3306 fechada ou inacessível.")

    except socket.timeout:
        status_placeholder.error("Timeout na conexão com o MySQL.")
    except Exception as e:
        st.error(f"Erro de diagnóstico na Sessão 14: {e}")
def s15_subdomain_discovery(dom):
    destacar_sessao("15", "DESCOBERTA DE SUBDOMÍNIOS (OSINT INTERNO)")
    
    # Sanitização rigorosa para extrair o domínio limpo
    alvo_base = dom.replace("https://", "").replace("http://", "").split('/')[0].strip()
    status_log(f"Iniciando descoberta paralela de subdomínios para: {alvo_base}...", "INFO")
    
    # Dicionário de alvos estendido para cobrir mais vetores comuns de ataque
    subdominios = [
        "www", "dev", "test", "staging", "api", "v1", "v2", 
        "admin", "mail", "portal", "shop", "blog", "vpn", 
        "corp", "monitor", "git", "jenkins", "auth", "db"
    ]
    
    # Elementos visuais dinâmicos para animação no Streamlit
    barra_progresso = st.progress(0)
    status_texto = st.empty()
    
    subdominios_encontrados = {}
    total_subs = len(subdominios)
    
    # Função interna para execução concorrente via Thread
    def scan_sub(sub):
        host_alvo = f"{sub}.{alvo_base}"
        try:
            # Tenta resolver o host diretamente pelo socket do sistema
            ip_resolvido = socket.gethostbyname(host_alvo)
            return host_alvo, ip_resolvido
        except socket.gaierror:
            return host_alvo, None

    st.write("### 🌐 Mapeamento de Superfície Exposta")
    
    # Bloco expansível onde os resultados vão "brotar" em tempo real durante o escaneamento
    with st.expander("🔍 Subdomínios Detectados (Atualizando Ativamente)", expanded=True):
        container_resultados = st.empty()
        
        # Dispara 6 trabalhadores em paralelo para acelerar o processo sem estressar o backend
        with ThreadPoolExecutor(max_workers=6) as executor:
            futuros = {executor.submit(scan_sub, s): s for s in subdominios}
            
            for idx, futuro in enumerate(as_completed(futuros)):
                host_processado, ip_resultado = futuro.result()
                
                if ip_resultado:
                    # Alimenta o dicionário caso o host responda
                    subdominios_encontrados[host_processado] = ip_resultado
                    
                    # Print técnico no terminal para manter seus logs clássicos do Kali ativos
                    print(f"\033[92m[+] Subdomínio encontrado: {host_processado} ({ip_resultado})\033[0m")
                    
                    # Atualiza a visualização interna do painel Streamlit na hora
                    with container_resultados.container():
                        st.success(f"🚀 *Ameaça Potencial:* Host ativo identificado!")
                        st.dataframe({
                            "Subdomínio Ativo": list(subdominios_encontrados.keys()),
                            "Endereço IP": list(subdominios_encontrados.values())
                        }, use_container_width=True)
                
                # Avança a barra de progresso dinamicamente
                progresso_atual = (idx + 1) / total_subs
                barra_progresso.progress(progresso_atual)
                status_texto.text(f"Progresso da Varredura: {int(progresso_atual * 100)}% concluído")

    # Finalização limpa dos componentes de carregamento
    barra_progresso.empty()
    status_texto.empty()

    # Exibição do relatório final consolidado
    if subdominios_encontrados:
        status_log(f"Varredura concluída. {len(subdominios_encontrados)} subdomínios expostos identificados.", "OK")
    else:
        status_log("Varredura concluída. Nenhum subdomínio alternativo mapeado.", "INFO")
        st.info("Nenhum subdomínio adicional foi detectado na lista de dicionário padrão.")

def s16_ct_logs_discovery(dom):
    st.markdown("---")
    st.markdown("### 🛰️ Sessão 16: Reconhecimento Passivo via CT Logs (Histórico SSL)")
    status_log(f"Interrogando registros globais de Certificados para: {dom}...", "INFO")
    
    alvo_limpo = dom.replace("https://", "").replace("http://", "").split('/')[0].strip()
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    subdominios_encontrados = set()
    sucesso = False

    # --- PLANO A: Executa o crt.sh ---
    url_crt = f"https://crt.sh/?q=%25.{alvo_limpo}&output=json"
    try:
        session = requests.Session()
        adapter = HTTPAdapter(max_retries=2)
        session.mount('https://', adapter)
        
        resposta = session.get(url_api=url_crt, headers=headers, timeout=10)
        
        if resposta.status_code == 200:
            dados_json = resposta.json()
            for registro in dados_json:
                name_value = registro.get('name_value', '')
                for sub in name_value.split('\n'):
                    sub_limpo = sub.strip().lower()
                    if sub_limpo and not sub_limpo.startswith('*'):
                        subdominios_encontrados.add(sub_limpo)
            sucesso = True
            st.success("✅ Dados obtidos com sucesso via crt.sh!")
            
    except Exception:
        # Se der qualquer erro no crt.sh (Timeout, 502, etc), o Python ignora e avança para o Plano B
        pass

    # --- PLANO B: Ativado automaticamente se o crt.sh falhar ---
    if not sucesso:
        st.warning("⚠️ Servidor principal (crt.sh) instável ou pesado. Ativando Plano B (Certspotter API)...")
        url_spotter = f"https://api.certspotter.com/v1/issuances?domain={alvo_limpo}&include_subdomains=true&expand=dns_names"
        
        try:
            resposta_b = requests.get(url_spotter, headers=headers, timeout=12)
            if resposta_b.status_code == 200:
                dados_json_b = resposta_b.json()
                for registro in dados_json_b:
                    dns_names = registro.get('dns_names', [])
                    for sub in dns_names:
                        sub_limpo = sub.strip().lower()
                        # Garante que só pega subdomínios relacionados ao alvo
                        if alvo_limpo in sub_limpo and not sub_limpo.startswith('*'):
                            subdominios_encontrados.add(sub_limpo)
                sucesso = True
                st.success("✅ Dados obtidos com sucesso via Certspotter API!")
        except Exception as e:
            st.error(f"❌ Ambos os servidores de CT Logs falharam ou deram timeout: {e}")

    # --- EXIBIÇÃO DOS RESULTADOS NA TELA ---
    if sucesso:
        st.write("### 📋 Subdomínios Históricos Identificados (100% Passivo)")
        if subdominios_encontrados:
            lista_ordenada = sorted(list(subdominios_encontrados))
            st.metric(label="Total de Subdomínios Reais Descobertos", value=len(lista_ordenada))
            st.dataframe({"Domínio / Subdomínio Mapeado": lista_ordenada}, use_container_width=True)
        else:
            st.warning("Nenhum registro público de subdomínio foi localizado para este alvo.")
# --------------------------------------------------------------------------------
# BANNER E FLUXO PRINCIPAL
# --------------------------------------------------------------------------------
def main():
    # --- 1. ESTILIZAÇÃO DA BARRA LATERAL E METADADOS DOS LOGS ---
    st.sidebar.markdown(f"Pesquisador: {NICK}")
    st.sidebar.markdown(f"Versão: {VERSAO}")
    st.sidebar.markdown(f"Início: {st.session_state.hora_inicio}")
    activar_hash_audit = st.sidebar.checkbox("📂 Incluir Identificador de Hash (Sessão 11)", value=True)
    
    st.markdown("---")

    # --- 2. ENTRADA UNIFICADA DO ALVO INTEGRADA COM A SESSÃO 10 ---
    # Busca o valor existente ou define o padrão seguro
    alvo_salvo = st.session_state.get('url_alvo', '')
    if not alvo_salvo:
        alvo_salvo = "exemplo.com"

    # O próprio Streamlit grava na memória automaticamente através do parâmetro key
    st.text_input(
        "Defina o Alvo (URL/IP):", 
        value=alvo_salvo, 
        key='url_alvo'
    )

    # --- 3. BOTÃO DE INICIALIZAÇÃO E SANITIZAÇÃO ---
    if st.button("Iniciar Auditoria Industrial Completa"):
        
        # Puxa o dado digitado direto da chave gerenciada pelo widget
        alvo_bruto = st.session_state.get('url_alvo', '').strip()
        
        if not alvo_bruto or alvo_bruto == "exemplo.com" or alvo_bruto == "":
            st.error("🚨 Por favor, insira um alvo válido para começar.")
            st.stop()
        
        # Faz a limpeza dos protocolos e caminhos extras
        dom = alvo_bruto.replace("https://", "").replace("http://", "").split('/')[0].strip()
        
        # Guardamos o domínio limpo em outra chave segura para uso das ferramentas internas
        st.session_state['alvo_limpo'] = dom
        
        # Dispara o gerenciador de status nativo do Streamlit usando o domínio higienizado
        with st.status(f"🔎 Auditoria em progresso: {dom}...", expanded=True) as status:
                
                # --- FASE 1: INTELIGÊNCIA PRÉVIA & RECON ---
                status.update(label="🔍 Fase 1: Consultando Inteligência (Shodan)...", state="running")
                try:
                    st.write("🔍 Consultando Inteligência (Shodan)...")
                    s0_inteligencia_shodan(dom)
                except Exception as e:
                    st.error(f"⚠️ Falha na Sessão Shodan: {e}")

                try:
                    st.write("⚙️ Calibrando motor de falso positivo...")
                    calibragem = calibrar_motor_llc(dom)
                except Exception as e:
                    st.error(f"⚠️ Falha na calibração do motor: {e}")
                    calibragem = None

                # --- FASE 2: INFRAESTRUTURA & DNS ---
                status.update(label="🌐 Fase 2: Mapeando Infraestrutura e Subdomínios...", state="running")
                try:
                    st.write("🌐 Mapeando Infraestrutura e Subdomínios...")
                    s1_recon_dns(dom)
                except Exception as e:
                    st.error(f"⚠️ Erro na Sessão 1 (DNS): {e}")

                try:
                    s2_geo_infra(dom)
                except Exception as e:
                    st.error(f"⚠️ Erro na Sessão 2 (GeoIP): {e}")

                try:
                    s15_subdomain_discovery(dom)
                except Exception as e:
                    st.error(f"⚠️ Erro na Sessão 15 (Subdomínios): {e}")
                
                try:
                    s16_ct_logs_discovery(dom)  # <-- Adiciona o novo braço de satélite passivo aqui!
                except Exception as e:
                    st.error(f"⚠️ Erro na Sessão 16 (CT Logs): {e}")
                # --- FASE 3: FINGERPRINT & CABEÇALHOS ---
                status.update(label="🛡️ Fase 3: Analisando Fingerprint e Cabeçalhos...", state="running")
                try:
                    st.write("🛡️ Analisando Fingerprint e Cabeçalhos...")
                    s3_fingerprint_tecnologico(dom)
                except Exception as e:
                    st.error(f"⚠️ Erro na Sessão 3 (Fingerprint): {e}")

                try:
                    s4_owasp_headers(dom)
                except Exception as e:
                    st.error(f"⚠️ Erro na Sessão 4 (OWASP Headers): {e}")

# --- FASE 4: FUZZING & PORT SCANNER ---
        status.update(label="🚙 Executando Motor de Fuzzing e Portas...", state="running")

        # Containers estáticos para segurar o layout da Fase 4
        bloco_fuzzing = st.container()
        bloco_portas = st.container()
        bloco_cookies = st.container()

        try:
            with bloco_fuzzing:
                s5_6_7_multi_fuzz(dom, calibragem)
        except Exception as e:
            st.error(f"⚠️ Erro no Fuzzing (5/6/7): {e}")

        try:
            with bloco_portas:
                s8_port_scanner(dom)
        except Exception as e:
            st.error(f"⚠️ Erro na Sessão 8 (Port Scanner): {e}")

        try:
            with bloco_cookies:
                s9_cookies_session(dom)
        except Exception as e:
            st.error(f"⚠️ Erro na Sessão 9 (Cookies): {e}")

        # --- FASE 5: SIMULAÇÃO DE VETORES DE AUTENTICAÇÃO & DB ---
        status.update(label="🔑 Testando Vetores de Autenticação e Exploração...", state="running")

        # Containers estáticos para segurar o layout da Fase 5
        bloco_auth_brute = st.container()
        bloco_sessao_12 = st.container()
        bloco_sessao_14 = st.container()

        try:
            with bloco_auth_brute:
                st.write("🔑 Testando Vetores de Autenticação e Brute-Force...")
                s13_bruteforce_simulation(dom)
        except Exception as e:
            st.error(f"⚠️ Erro na Sessão 13 (Brute-Force): {e}")

        # --- SESSÃO 12: Auditoria de Portas Administrativas ---
        try:
            with bloco_sessao_12:
                st.write("⚙️ Executando Auditoria de Portas Administrativas (Sessão 12) ...")
                s12_privilege_escalation_auditor(dom)
        except Exception as e:
            st.error(f"⚠️ Erro crítico na Sessão 12: {e}")

        # --- SESSÃO 14: Verificação de Root MySQL ---
        try:
            with bloco_sessao_14:
                st.write("🗄️ Iniciando Verificação de Root MySQL (Sessão 14) ...")
                s14_mysql_root_audit(dom)
        except Exception as e:
            st.error(f"⚠️ Erro na Sessão 14 (MySQL): {e}")
        # --- FASE 6: PROCESSAMENTO DE ASSINATURAS & LOGS ---
        if activar_hash_audit:
             status.update(label="📊 Analisando Assinaturas de Criptografia...", state="running")
        try:
             st.write("📊 Executando Identificador de Hash Avançado (Sessão 11)...")
             s11_identificador_hash(dom)
        except Exception as e:
            st.error(f"⚠️ Erro na Sessão 11 (Hash): {e}")

# --- SESSÃO FINAL: BOTÃO DE FINALIZAÇÃO ---
    if st.button("Finalizar Auditoria"):
        # 1. Recupera as informações essenciais
        alvo = st.session_state.get('url_alvo', '')
        log_completo = st.session_state.get('logs_completos', '')

        # 2. Executa a função e SALVA O RESULTADO na sessão (para não sumir)
        with st.spinner("🤖 IA processando dados..."):
            dados = analisar_logs_via_nuvem(log_completo, alvo)
            st.session_state['relatorio_dados'] = dados

    # 3. EXIBIÇÃO: Verifica se há dados na sessão e renderiza
    if 'relatorio_dados' in st.session_state and st.session_state['relatorio_dados']:
        dados = st.session_state['relatorio_dados']
        
        # Chama a função de exibição que desenha o relatório na tela
        # Note: removi a chamada da nuvem de dentro da função, 
        # pois já processamos acima
        renderizar_relatorio(dados)

# --- FUNÇÃO AUXILIAR DE RENDERIZAÇÃO (Coloque fora do main) ---
def renderizar_relatorio(dados):
    st.markdown("---")
    st.subheader("📊 Relatório de Auditoria")
    st.metric("Alvo Identificado", dados.get("alvo", "Não informado"))
    
    st.markdown("### 📝 Análise Técnica")
    st.info(dados.get("resumo_executivo", "Sem resumo."))
    
    st.markdown("### ⚠️ Nível de Risco")
    st.warning(dados.get("nivel_risco_geral", "Sem classificação."))
    
    # --- NOVO BLOCO PARA VULNERABILIDADES E REMEDIAÇÕES ---
    st.markdown("### 🛡️ Vulnerabilidades Detectadas")
    vulns = dados.get("vulnerabilidades_detectadas", [])
    
    if vulns:
        for v in vulns:
            with st.expander(f"Falha: {v.get('vulnerabilidade', 'Desconhecido')}"):
                st.write(f"**Severidade:** {v.get('severidade', 'N/A')}")
                st.write(f"**Detalhes:** {v.get('detalhes_tecnicos', 'N/A')}")
                st.write(f"**✅ Remediação:** {v.get('mitigacao', 'N/A')}")
    else:
        st.write("Nenhuma vulnerabilidade específica detectada nos logs.")

    st.success("Fim do relatório.")

# 1. Transforma o dicionário de dados no arquivo PDF físico em memória
    arquivo_pdf_bytes = gerar_pdf_relatorio(dados, dados.get('alvo', 'alvo_analisado'))

    # 2. Cria o botão para fazer o download do PDF no Streamlit
    st.download_button(
        label="📥 Baixar Relatório Técnico Oficial (PDF)",
        data=arquivo_pdf_bytes,
        file_name=f"relatorio_auditoria_{dados.get('alvo', 'scan')}.pdf",
        mime="application/pdf"
    )
if __name__ == "__main__":
    main()
