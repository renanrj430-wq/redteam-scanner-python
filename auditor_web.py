#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FERRAMENTA: RED TEAM AUDITOR PRO - V36.0 (INDUSTRIAL ENGINE)
AUTOR: RENAN ALVES DA SILVA (@renan_security_researcher)
LOCALIZAÇÃO: RIO DE JANEIRO, BR | 2026
TECNOLOGIA: LLC TECHNOLOGY (LOGIC LLC) | OFFENSIVE SECURITY
AVISO: Uso estritamente educacional e para auditorias autorizadas.
"""

import requests
import socket
import ssl
import time
import sys
import os
import uuid
import re
import random
import json
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from colorama import Fore, Style, init

# --- INICIALIZAÇÃO E AMBIENTE ---
init(autoreset=True)

NICK = "renan_security_researcher"
VERSAO = "36.0"
TIMEOUT_GLOBAL = 15
THREADS_MOTOR = 15  # Otimizado para arquiteturas modernas (6 Cores)
HORA_INICIO = datetime.now().strftime('%d/%m/%Y %H:%M:%S')

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

UA_LIST = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0'
]

WL_DIR = [
    ".env", ".git/config", "admin/", "backup/", "db.sql", "config.php", ".ssh/id_rsa", 
    "console/", ".docker/config.json", "setup.php", "phpinfo.php", "v1/.env", 
    "backup.zip", "wp-config.php.bak", "configuration.php", "settings.py", 
    "web.config", ".htaccess", "backup.tar.gz", "old-index.php", "test.php", 
    "sql.php", "info.php", "database.yml", "docker-compose.yml", ".env.old", 
    "server-status", "dashboard/", "cp/", "control/", "manager/", "logs/",
    "private/", "database.sql", "backup.sql", "dump.sql", "config.bak",
    ".aws/config", ".npmrc", ".bash_history", "etc/passwd", "proc/self/environ",
    "web-console/", "invoker/", "jmx-console/", "administrator/", "vnc.log",
    "../../../../etc/passwd", "cgi-bin/config.sh", "shell.php?cmd=id", "v1/debug/env"
]

WL_API = [
    "api/v1/user", "v2/auth", "swagger.json", "graphQL", "rest-api/v1/", 
    "v1/config", "api/status", "internal/v1", "api/v1/debug", "api/docs", 
    "v3/health", "api/v1/backup", "v1/list", "api/v2/users", "api/v1/cron", 
    "api/export", "api/v1/settings", "v1/debug/vars", "api/v1/db", "auth/login",
    "api/v2/db/config", "api/v1/metrics", "api/v1/cloud/credentials",
    "api/v1/user/1", "api/v1/user/admin", "api/v2/payments", "api/v1/logs"
]

WL_NUVEM = [
    ".aws/credentials", "s3-config", "k8s/", "firebase.json", "cloud-config.yaml", 
    ".azure/credentials", "metadata", "gsutil/config", "storage-key.json", 
    "client_secret.json", "credentials.json", "service-account.json", 
    "access_key", "deployment.yaml", "cluster-info", "kube-config", "pods/",
    "terraform.tfstate", "vault-token", "jenkins.config.xml"
]

# --- FUNÇÕES DE INTERFACE ---

def status_log(mensagem, tipo="INFO"):
    hora = datetime.now().strftime('%H:%M:%S')
    cores = {"INFO": Fore.CYAN, "OK": Fore.GREEN, "WARN": Fore.YELLOW, "FAIL": Fore.RED}
    cor = cores.get(tipo, Fore.WHITE)
    print(f"{cor}[{hora}] {Fore.WHITE}STATUS: {mensagem}")

def destacar_sessao(numero, titulo):
    linha = "═" * 45
    print(f"\n{Fore.YELLOW}{Style.BRIGHT}{linha} [ SESSÃO {numero}: {titulo} ] {linha}")
    time.sleep(0.3)

def exibir_alerta(secao, alvo, impacto, extraido=None):
    print(f"\n{Fore.RED}{Style.BRIGHT}┌{'─'*95}┐")
    print(f"{Fore.RED}{Style.BRIGHT}│ [!] FALHA DE SEGURANÇA DETECTADA - {secao.upper()}")
    print(f"{Fore.RED}{Style.BRIGHT}├{'─'*95}┤")
    print(f"{Fore.WHITE}│ ALVO AFETADO   : {Fore.CYAN}{alvo}")
    print(f"{Fore.WHITE}│ IMPACTO ESTIMADO: {Fore.YELLOW}{impacto}")
    if extraido:
        print(f"{Fore.GREEN}{Style.BRIGHT}│ DADOS EXTRAÍDOS : {extraido}")
    print(f"{Fore.RED}{Style.BRIGHT}└{'─'*95}┘")

# --- MOTOR DE INTELIGÊNCIA ---

def analisador_profundo(html):
    achados = []
    regex_map = {
        "CRITICAL_LFI": r"root:x:0:0",
        "CRITICAL_RCE": r"(uid=[0-9]+\(.*\))",
        "DB_STR": r"(?:mongodb\+srv|postgres|mysql|redis):\/\/[^\s']+",
        "API_KEY": r"(?:api|secret|token|key|pass)[_-]?(\w{10,45})",
        "AWS_AUTH": r"AKIA[0-9A-Z]{16}",
        "JWT_TOKEN": r"eyJ[A-Za-z0-9-_=]+\.eyJ[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*",
        "EMAIL_SENS": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    }
    for chave, regex in regex_map.items():
        m = re.search(regex, html, re.IGNORECASE)
        if m: achados.append(f"{chave}: {m.group(0)[:35]}...")
    return " | ".join(achados) if achados else None

def calibrar_motor_llc(domain):
    destacar_sessao("0", "CALIBRAGEM LLC (LOGIC LLC)")
    status_log("Mapeando comportamento do alvo contra Falsos Positivos...")
    try:
        url_falsidade = f"http://{domain}/{uuid.uuid4().hex[:12]}"
        h = {'User-Agent': random.choice(UA_LIST)}
        r = requests.get(url_falsidade, headers=h, timeout=10, verify=False, allow_redirects=True)
        tamanho_base = len(r.content) if r.content else 0
        server_rg = r.headers.get('Server', 'Desconhecido')
        status_log(f"Assinatura LLC capturada: {tamanho_base} bytes.", "OK")
        status_log(f"Identidade do Servidor (RG): {server_rg}", "INFO")
        return {"ativo": True, "tamanho": tamanho_base, "server": server_rg}
    except:
        status_log("Calibragem falhou. Usando detecção básica.", "WARN")
        return {"ativo": False, "tamanho": 0, "server": "Desconhecido"}

def core_fuzzing_worker(url, cal, secao):
    try:
        h = {
            'User-Agent': random.choice(UA_LIST),
            'Accept': '*/*',
            'Connection': 'keep-alive',
            'Referer': f'https://google.com.br/search?q={uuid.uuid4().hex}'
        }
        r = requests.get(url, headers=h, timeout=TIMEOUT_GLOBAL, verify=False, allow_redirects=False)
        
        if r.status_code == 200:
            tamanho_atual = len(r.content) if r.content else 0
            
            # FILTRO DE EFICIÊNCIA INDUSTRIAL
            if tamanho_atual < 200:
                return

            if cal["ativo"] and abs(tamanho_atual - cal["tamanho"]) < 150:
                return
            
            segredos = analisador_profundo(r.text)
            
            if "etc/passwd" in url and not (segredos and "CRITICAL_LFI" in segredos):
                return
            
            if ".env" in url and "=" not in r.text:
                return

            print(f"    {Fore.GREEN}[+] {secao} ENCONTRADA: {Fore.WHITE}{url} {Fore.GREEN}(Bytes: {tamanho_atual})")
            
            impacto = "Arquivo sensível exposto publicamente."
            if segredos and "CRITICAL" in segredos:
                impacto = "CRÍTICO: Vulnerabilidade de Execução ou Acesso ao Sistema!"
            
            exibir_alerta(secao, url, impacto, segredos)
    except: pass

# --- SESSÕES EXECUTIVAS ---

def s1_recon_dns(dom):
    destacar_sessao("1", "RECONHECIMENTO DNS")
    try:
        ip = socket.gethostbyname(dom)
        status_log(f"Alvo resolvido: {ip}", "OK")
    except: status_log("Falha na resolução de DNS.", "FAIL")

def s2_geo_infra(dom):
    destacar_sessao("2", "INFRAESTRUTURA E GEO-IP")
    try:
        ip = socket.gethostbyname(dom)
        info = requests.get(f"http://ip-api.com/json/{ip}", timeout=5).json()
        print(f"    - LOCALIZAÇÃO: {info.get('city')}, {info.get('country')}")
        print(f"    - PROVEDOR   : {info.get('isp')} | ASN: {info.get('as')}")
    except: status_log("Dados de geolocalização indisponíveis.", "WARN")

def s4_owasp_headers(dom):
    destacar_sessao("4", "CABEÇALHOS DE SEGURANÇA (OWASP)")
    status_log("Validando políticas contra Injeção e Clickjacking...")
    try:
        r = requests.get(f"http://{dom}", timeout=5, verify=False)
        for h in ["Content-Security-Policy", "X-Frame-Options", "X-Content-Type-Options"]:
            if h in r.headers:
                print(f"    {Fore.GREEN}[V] {h}: Proteção Ativa.")
    except: pass

def s5_6_7_multi_fuzz(dom, cal):
    destacar_sessao("5/6/7", "MOTOR DE FUZZING PARALELO")
    status_log(f"Iniciando auditoria com {THREADS_MOTOR} threads (Modo Industrial)...")
    full_list = [(p, "DIRETÓRIO") for p in WL_DIR] + [(p, "API") for p in WL_API] + [(p, "CLOUD") for p in WL_NUVEM]
    with ThreadPoolExecutor(max_workers=THREADS_MOTOR) as ex:
        for path, tipo in full_list:
            ex.submit(core_fuzzing_worker, f"http://{dom}/{path}", cal, tipo)

def s8_port_scanner(dom):
    destacar_sessao("8", "VARREDURA DE PORTAS OPERACIONAIS")
    portas = [21, 22, 23, 25, 80, 110, 443, 1433, 3306, 3389, 5432, 8080, 8443]
    for p in portas:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.7)
            if s.connect_ex((dom, p)) == 0:
                exibir_alerta("Sessão 8", f"Porta {p}", "Serviço exposto publicamente.")
            s.close()
        except: pass

def s9_final_summary(dom):
    print(f"\n{Fore.CYAN}{Style.BRIGHT}{'═' * 110}")
    print(f"{Fore.WHITE} RELATÓRIO FINAL DE AUDITORIA - {HORA_INICIO}")
    print(f"{Fore.WHITE} ALVO ANALISADO  : {Fore.YELLOW}{dom}")
    print(f"{Fore.WHITE} PESQUISADOR     : {Fore.WHITE}{NICK}")
    print(f"{Fore.GREEN}{Style.BRIGHT}[+] OPERAÇÃO CONCLUÍDA. V36 OPERADA COM SUCESSO.")
    print(f"{Fore.CYAN}{Style.BRIGHT}{'═' * 110}")

def banner_principal():
    os.system('clear' if os.name == 'posix' else 'cls')
    art = """  ██████╗ ███████╗██████╗     ████████╗███████╗ █████╗ ███╗   ███╗
  ██╔══██╗██╔════╝██╔══██╗    ╚══██╔══╝██╔════╝██╔══██╗████╗ ████║
  ██████╔╝█████╗  ██║  ██║       ██║   █████╗  ███████║██╔████╔██║
  ██╔══██╗██╔════╝██║  ██║       ██║   ██╔════╝██╔══██║██║╚██╔╝██║
  ██║  ██║███████╗██████╔╝       ██║   ███████╗██║  ██║██║ ╚═╝ ██║
  ╚═╝  ╚═╝╚══════╝╚═════╝        ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝"""
    print(f"{Fore.RED}{Style.BRIGHT}{art}")
    print(f"  {Fore.WHITE}V{VERSAO} | RED TEAM AUDITOR | BY: {NICK} | RIO DE JANEIRO")
    print(f"{Fore.CYAN}{'═' * 100}\n")

def main():
    banner_principal()
    alvo_raw = input(f"{Fore.WHITE}Defina o alvo (empresa.com.br): ").strip().lower()
    if not alvo_raw: return
    dom = alvo_raw.replace("https://","").replace("http://","").split('/')[0].split(':')[0]
    calibragem = calibrar_motor_llc(dom)
    s1_recon_dns(dom)
    s2_geo_infra(dom)
    s4_owasp_headers(dom)
    s5_6_7_multi_fuzz(dom, calibragem)
    s8_port_scanner(dom)
    s9_final_summary(dom)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}[!] Auditoria interrompida pelo operador.")
        sys.exit()
