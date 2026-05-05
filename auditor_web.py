#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FERRAMENTA: RED TEAM AUDITOR PRO - V36.1 (INDUSTRIAL ENGINE)
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
import hashid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from colorama import Fore, Style, init

# --- INICIALIZAÇÃO E AMBIENTE ---
init(autoreset=True)

NICK = "renan_security_researcher"
VERSAO = "36.0"
TIMEOUT_GLOBAL = 15
THREADS_MOTOR = 25  
HORA_INICIO = datetime.now().strftime('%d/%m/%Y %H:%M:%S')

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- WORDLISTS TÁTICAS EXPANDIDAS ---

UA_LIST = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Googlebot/2.1 (+http://www.google.com/bot.html)',
    'Mozilla/5.0 (compatible; Bingbot/2.0; +http://www.bing.com/bingbot.htm)',
    'DuckDuckBot/1.0; (+http://duckduckgo.com/duckduckbot.html)'
]

WL_DIR = [
    ".env", ".env.old", ".env.bak", ".env.example", ".git/config", ".git/index", 
    "admin/", "administrator/", "admin/config.php", "admin/db.php", "backup/", 
    "backup.sql", "backup.zip", "backup.tar.gz", "db.sql", "database.sql", 
    "config.php", "config.php.bak", "config.inc", "config.old", ".ssh/id_rsa", 
    "console/", ".docker/config.json", "setup.php", "phpinfo.php", "v1/.env", 
    "wp-config.php", "wp-config.php.bak", "configuration.php", "settings.py", 
    "web.config", ".htaccess", "old-index.php", "test.php", "sql.php", "info.php", 
    "database.yml", "docker-compose.yml", "server-status", "dashboard/", "cp/", 
    "control/", "manager/", "logs/", "private/", "dump.sql", "config.bak",
    ".aws/config", ".npmrc", ".bash_history", "etc/passwd", "proc/self/environ",
    "web-console/", "invoker/", "jmx-console/", "vnc.log", "cgi-bin/config.sh", 
    "shell.php", "cmd.php", "v1/debug/env", "../../etc/passwd", "/.git/HEAD"
]

WL_API = [
    "api/v1/user", "api/v1/auth", "v2/auth", "swagger.json", "graphQL", 
    "rest-api/v1/", "v1/config", "api/status", "internal/v1", "api/v1/debug", 
    "api/docs", "v3/health", "api/v1/backup", "v1/list", "api/v2/users", 
    "api/v1/cron", "api/export", "api/v1/settings", "v1/debug/vars", "api/v1/db", 
    "auth/login", "api/v2/db/config", "api/v1/metrics", "api/v1/cloud/credentials",
    "v1/internal/config", "api/v1/env", "api/v1/logs"
]

WL_NUVEM = [
    ".aws/credentials", "s3-config", "k8s/", "firebase.json", "cloud-config.yaml", 
    ".azure/credentials", "metadata", "gsutil/config", "storage-key.json", 
    "client_secret.json", "credentials.json", "service-account.json", 
    "access_key", "deployment.yaml", "terraform.tfstate", "vault-token"
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

def exibir_alerta(secao, alvo, impacto_cliente, mapa_mina, ferra_ataque, extraido=None):
    print(f"\n{Fore.RED}{Style.BRIGHT}┌{'─'*95}┐")
    print(f"{Fore.RED}{Style.BRIGHT}│ [!] FALHA DE SEGURANÇA DETECTADA - {secao.upper()}")
    print(f"{Fore.RED}{Style.BRIGHT}├{'─'*95}┤")
    print(f"{Fore.WHITE}│ ALVO AFETADO      : {Fore.CYAN}{alvo}")
    print(f"{Fore.WHITE}│ IMPACTO CLIENTE   : {Fore.YELLOW}{impacto_cliente}")
    print(f"{Fore.MAGENTA}│ MAPA DA MINA      : {Fore.WHITE}{mapa_mina}")
    print(f"{Fore.BLUE}{Style.BRIGHT}│ FERRAMENTA ATAQUE : {Fore.WHITE}{ferra_ataque}")
    if extraido:
        print(f"{Fore.GREEN}{Style.BRIGHT}│ DADOS EXTRAÍDOS    : {extraido}")
    print(f"{Fore.RED}{Style.BRIGHT}└{'─'*95}┘")
def detectar_hash(alvo):
    hd = hashid.HashID()
    identificacoes = list(hd.identifyHash(alvo))
    return identificacoes
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
        "GOOGLE_KEY": r"AIza[0-9A-Za-z-_]{35}"
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
        return {"ativo": True, "tamanho": tamanho_base, "server": server_rg}
    except:
        status_log("Calibragem falhou. Usando detecção básica.", "WARN")
        return {"ativo": False, "tamanho": 0, "server": "Desconhecido"}

# --- SESSÕES OPERACIONAIS ---

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

def s3_fingerprint_tecnologico(dom):
    destacar_sessao("3", "FINGERPRINT E BANNER GRABBING")
    status_log("Interrogando cabeçalhos para identificar WAF e Infra...")
    try:
        r = requests.get(f"http://{dom}", timeout=5, verify=False, headers={'User-Agent': random.choice(UA_LIST)})
        server = r.headers.get('Server', 'Não detectado')
        pow_by = r.headers.get('X-Powered-By', 'Não detectado')
        
        waf_hits = []
        if any(h in r.headers for h in ["X-Vercel-Id", "X-Vercel-Cache"]): waf_hits.append("Vercel Edge")
        if "CF-RAY" in r.headers: waf_hits.append("Cloudflare WAF")
        if "X-Akamai-Transformed" in r.headers: waf_hits.append("Akamai WAF")
        if "x-amz-id-2" in r.headers: waf_hits.append("AWS S3/CloudFront")
        
        print(f"    [+] BANNER DO SERVIDOR: {Fore.CYAN}{server}")
        print(f"    [+] TECNOLOGIA BASE   : {Fore.CYAN}{pow_by}")
        if waf_hits:
            print(f"    [+] WAF/INFRA DETECTADA: {Fore.YELLOW}{' | '.join(waf_hits)}")
        else:
            print(f"    [+] PROTEÇÃO WAF      : {Fore.RED}Não identificado")
    except: status_log("Erro no fingerprinting.", "FAIL")

def s4_owasp_headers(dom):
    destacar_sessao("4", "CABEÇALHOS DE SEGURANÇA (OWASP)")
    status_log("Validando políticas contra Injeção e Clickjacking...")
    try:
        r = requests.get(f"http://{dom}", timeout=5, verify=False, headers={'User-Agent': random.choice(UA_LIST)})
        headers_map = {
            "Content-Security-Policy": "Risco de XSS.",
            "X-Frame-Options": "Permite Clickjacking.",
            "X-Content-Type-Options": "MIME Sniffing ativado."
        }
        for h, erro in headers_map.items():
            if h in r.headers:
                print(f"    {Fore.GREEN}[V] {h}: Proteção Ativa.")
            else:
                exibir_alerta("Sessão 4", dom, f"Ausência de {h}", erro, "Configurar Header.")
    except: pass

def core_fuzzing_worker(url, cal, secao):
    try:
        fake_ip = f"{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}"
        h = {'User-Agent': random.choice(UA_LIST), 'X-Forwarded-For': fake_ip, 'Referer': 'https://www.google.com/'}
        r = requests.get(url, headers=h, timeout=TIMEOUT_GLOBAL, verify=False, allow_redirects=False)
        if r.status_code == 200:
            t_atual = len(r.content) if r.content else 0
            if t_atual < 200 or (cal["ativo"] and abs(t_atual - cal["tamanho"]) < 150): return
            segredos = analisador_profundo(r.text)
            exibir_alerta(secao, url, "Vazamento estrutural.", "Diretório exposto.", "Manual exploit", segredos)
    except: pass

def s5_6_7_multi_fuzz(dom, cal):
    destacar_sessao("5/6/7", "MOTOR DE FUZZING PARALELO (CAMALEÃO)")
    status_log(f"Iniciando auditoria industrial com {THREADS_MOTOR} threads...")
    full_list = [(p, "DIRETÓRIO") for p in WL_DIR] + [(p, "API") for p in WL_API] + [(p, "CLOUD") for p in WL_NUVEM]
    with ThreadPoolExecutor(max_workers=THREADS_MOTOR) as ex:
        for path, tipo in full_list:
            ex.submit(core_fuzzing_worker, f"http://{dom}/{path}", cal, tipo)

def s8_port_scanner(dom):
    destacar_sessao("8", "VARREDURA DE PORTAS OPERACIONAIS")
    portas = [21, 22, 23, 25, 80, 443, 3306, 3389, 5432, 8080, 8443]
    for p in portas:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.8)
            if s.connect_ex((dom, p)) == 0:
                exibir_alerta("Sessão 8", f"Porta {p}", "Serviço exposto.", "Vetor de brute-force.", f"Nmap -p {p}")
            s.close()
        except: pass

def s9_cookies_session(dom):
    destacar_sessao("9", "ANÁLISE DE COOKIES E SESSÃO")
    try:
        r = requests.get(f"http://{dom}", timeout=5, verify=False)
        if r.cookies:
            for c in r.cookies:
                secure = "SIM" if c.secure else "NÃO"
                httponly = "SIM" if c.has_nonstandard_attr('HttpOnly') else "NÃO"
                print(f"    [+] COOKIE: {Fore.MAGENTA}{c.name} {Fore.WHITE}| HttpOnly: {httponly} | Secure: {secure}")
        else: status_log("Nenhum cookie detectado.", "INFO")
    except: pass

def s10_log_final(dom):
    destacar_sessao("10", "FINALIZAÇÃO E LOG DE AUDITORIA")
    print(f"\n{Fore.GREEN}{Style.BRIGHT}[+] CICLO DE AUDITORIA COMPLETO: {dom}")
    print(f"{Fore.WHITE}PESQUISADOR : {NICK}")
    print(f"{Fore.CYAN}{'═' * 100}")

def s11_identificador_hash(hash_input):
    destacar_sessao("11", "IDENTIFICADOR DE HASH")
    try:
        tamanho = len(hash_input)
        if tamanho == 32:
            print(f"{Fore.GREEN}[+] Tipo provável: MD5")
        elif tamanho == 40:
            print(f"{Fore.GREEN}[+] Tipo provável: SHA1")
        elif tamanho == 64:
            print(f"{Fore.GREEN}[+] Tipo provável: SHA256")
        else:
            print(f"{Fore.RED}[!] Formato de hash desconhecido.")
    except Exception as e:
        print(f"{Fore.RED}[!] Erro: {e}")

def banner_principal():
    os.system('clear' if os.name == 'posix' else 'cls')
    art = f"""{Fore.RED}{Style.BRIGHT}
  ██████╗ ███████╗██████╗     ████████╗███████╗ █████╗ ███╗   ███╗
  ██╔══██╗██╔════╝██╔══██╗    ╚══██╔══╝██╔════╝██╔══██╗████╗ ████║
  ██████╔╝█████╗  ██║  ██║       ██║   █████╗  ███████║██╔████╔██║
  ██╔══██╗██╔════╝██║  ██║       ██║   ██╔════╝██╔══██║██║╚██╔╝██║
  ██║  ██║███████╗██████╔╝       ██║   ███████╗██║  ██║██║ ╚═╝ ██║
  ╚═╝  ╚═╝╚══════╝╚═════╝        ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝
    """
    print(art)
    print(f"  {Fore.WHITE}V{VERSAO} | RED TEAM AUDITOR | AUTHOR: {NICK} | RIO DE JANEIRO")
    print(f"{Fore.CYAN}{'═' * 100}\n")

def main():
    banner_principal()
    alvo_raw = input(f"{Fore.WHITE}Defina o alvo: ").strip().lower()
    if not alvo_raw: return
    dom = alvo_raw.replace("https://","").replace("http://","").split('/')[0]
    calibragem = calibrar_motor_llc(dom)
    s1_recon_dns(dom)
    s2_geo_infra(dom)
    s3_fingerprint_tecnologico(dom)
    s4_owasp_headers(dom)
    s5_6_7_multi_fuzz(dom, calibragem)
    s8_port_scanner(dom)
    s9_cookies_session(dom)
    s10_log_final(dom)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit()
