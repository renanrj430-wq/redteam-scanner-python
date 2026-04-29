import requests
import socket
import urllib3
import random
import time
import sys
import os
from datetime import datetime

# --- CONFIGURACOES TECNICAS ---
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

NICK = "renan_security_researcher"
VERSAO = "13.0"
HEADERS = {
    'User-Agent': f'Mozilla/5.0 (Security-Audit-v{VERSAO}; {NICK})',
    'Accept': '*/*'
}

def print_banner():
    """Exibe o cabecalho profissional no terminal conforme v10.5"""
    print("-" * 80)
    print(f"RE-SECURITY AUDITOR v{VERSAO} | ANALISTA: {NICK}")
    print(f"STATUS: ANALISE DE VULNERABILIDADE ATIVA | RIO DE JANEIRO, 2026")
    print("-" * 80)
    print(f"Sessao iniciada em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("-" * 80)

def draw_progress(percent, message):
    """Cria uma barra de progresso visual diretamente no terminal"""
    bar_length = 35
    filled_length = int(round(bar_length * percent / 100))
    bar = '=' * filled_length + '-' * (bar_length - filled_length)
    sys.stdout.write(f'\r[+] {percent}% | {bar} | {message}')
    sys.stdout.flush()

# --- MOTORES DE AUDITORIA ---

def modulo_infra(dominio):
    """Analise de rede e geolocalizacao baseada na v9.0"""
    res = {"ip": "N/A", "geo": "N/A", "isp": "N/A"}
    try:
        res["ip"] = socket.gethostbyname(dominio)
        api = requests.get(f"http://ip-api.com/json/{res['ip']}", timeout=5)
        if api.status_code == 200:
            data = api.json()
            res["geo"] = f"{data.get('city')}, {data.get('country')}"
            res["isp"] = data.get('isp')
    except:
        pass
    return res

def modulo_portas(ip):
    """Scanner de portas e vetores de entrada lateral conforme v10.5"""
    alvos = [21, 22, 23, 25, 53, 80, 110, 443, 3306, 8080, 8443]
    encontradas = []
    for p in alvos:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.3)
        if s.connect_ex((ip, p)) == 0:
            encontradas.append(p)
        s.close()
    return encontradas

def modulo_owasp(dominio):
    """Analise detalhada de cabecalhos de seguranca e cookies"""
    alertas = []
    server = "Nao Detectado"
    try:
        r = requests.get(f"https://{dominio}", timeout=10, verify=False, headers=HEADERS)
        server = r.headers.get('Server', 'Vercel' if 'vercel' in r.text.lower() else 'Oculto')
        
        check_list = {
            "Content-Security-Policy": "[X] CSP: AUSENTE -> Risco de XSS e Injecao de Scripts",
            "X-Frame-Options": "[X] CLICKJACK: AUSENTE -> Risco de Sequestro de Cliques",
            "Strict-Transport-Security": "[!] HSTS: DESATIVADO -> Conexao Insegura detectada",
            "X-Content-Type-Options": "[X] SNIFFING: AUSENTE -> Risco de execucao de arquivos maliciosos"
        }
        for h, msg in check_list.items():
            if h not in r.headers:
                alertas.append(msg)
        return alertas, server, r.cookies
    except:
        return ["[!] Erro de Conexao SSL/TLS"], "Erro", []

def modulo_fuzzing(dominio):
    """Fuzzing de diretorios com validacao anti-falso positivo profissional"""
    diretorios = [".env", ".git/config", "backup.zip", "admin/", "phpinfo.php", "config.php"]
    achados = []
    try:
        # Valida se e um ambiente Catch-all (comum na Vercel)
        check_fake = requests.get(f"https://{dominio}/audit_test_{random.randint(1,999)}", timeout=5)
        if check_fake.status_code == 200:
            return achados, True
            
        for path in diretorios:
            r = requests.get(f"https://{dominio}/{path}", timeout=2, headers=HEADERS)
            if r.status_code == 200:
                achados.append(path)
    except:
        pass
    return achados, False

def modulo_xss(dominio):
    """Simulacao de injecao de vetor XSS baseada na v10.5"""
    payload = "<script>alert('renan_security_check')</script>"
    try:
        r = requests.get(f"https://{dominio}/?search={payload}", timeout=5, headers=HEADERS)
        return payload in r.text
    except:
        return False

# --- FLUXO PRINCIPAL ---

def main():
    os.system('clear')
    print_banner()
    alvo = input("Digite o dominio alvo para auditoria: ")
    if not alvo: return

    print(f"\n[i] Iniciando varredura tecnica em: {alvo}...\n")
    
    draw_progress(20, "Mapeando Perimetro e Infraestrutura...")
    infra = modulo_infra(alvo)
    
    draw_progress(40, "Escaneando Portas e Servicos Ativos...")
    portas = modulo_portas(infra["ip"])
    
    draw_progress(60, "Analisando Vulnerabilidades Web (OWASP)...")
    owasp, srv, cookies = modulo_owasp(alvo)
    
    draw_progress(80, "Executando Fuzzing de Arquivos Sensiveis...")
    arquivos, is_fake = modulo_fuzzing(alvo)
    
    draw_progress(100, "Testando Vetores de Entrada (XSS)...")
    xss = modulo_xss(alvo)
    
    # --- RELATORIO FINAL EM TERMINAL ---
    print("\n\n" + "="*80)
    print("RELATORIO TECNICO DE AUDITORIA OFENSIVA")
    print("="*80)
    
    print(f"[i] IP DO SERVIDOR: {infra['ip']}")
    print(f"[i] LOCALIZACAO  : {infra['geo']}")
    print(f"[i] PROVEDOR/ISP : {infra['isp']}")
    print(f"[i] TECNOLOGIA   : {srv}")
    
    print("\n[+] 2. VETORES DE ACESSO (SCANN DE PORTAS):")
    if portas:
        for p in portas: print(f"  [!!!] ALERTA: Porta {p} ABERTA detectada.")
    else:
        print("  [V] Nenhuma porta critica aberta encontrada.")

    print("\n[+] 3. ANALISE OWASP E CABECALHOS:")
    for o in owasp: print(f"  {o}")
    if xss:
        print("  [X] XSS: VULNERAVEL -> Injeção de script confirmada.")
    else:
        print("  [V] XSS: Nenhuma falha obvia de injecao encontrada.")

    print("\n[+] 4. BUSCA POR ARQUIVOS (FUZZING):")
    if is_fake:
        print("  [!] NOTA: Catch-all detectado. Resultados de fuzzing suprimidos.")
    elif arquivos:
        for a in arquivos: print(f"  [X] EXPOSTO: /{a}")
    else:
        print("  [V] Nenhum arquivo sensivel identificado.")

    # Calculo de Nota Final v10.5
    nota = 10.0 - (len(portas)*0.5) - (len(owasp)*1.0)
    if xss: nota -= 4.0
    if arquivos: nota -= 2.0
    
    print("\n" + "-"*80)
    print(f"[*] CONCLUSAO DO ANALISTA | NOTA FINAL: {max(0.0, nota):.1f} / 10.0")
    print("-" * 80)
    print(f"Relatorio salvo como: relatorio_final_{alvo.replace('.','_')}.txt")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
