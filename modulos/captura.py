# --- modulos/captura.py ---
import requests

def extrair_contexto_alvo(alvo):
    """
    Faz uma requisição rápida ao alvo para identificar o servidor real (Vercel, Nginx, etc.)
    e o status dos cabeçalhos OWASP para que a IA não gere falsos positivos.
    """
    # Garante que o alvo tenha o protocolo correto
    url = alvo if alvo.startswith(("http://", "https://")) else f"https://{alvo}"
    
    servidor_detectado = "Não identificado"
    status_csp = "NÃO DETECTADO"
    status_xframe = "NÃO DETECTADO"
    status_xcontent = "NÃO DETECTADO"

    try:
        # Faz uma requisição HEAD ou GET rápida (apenas cabeçalhos) com timeout curto
        resposta = requests.get(url, timeout=5, allow_redirects=True)
        headers = resposta.headers

        # 1. Captura o Servidor Web dinamicamente
        servidor_detectado = headers.get("Server", "Não identificado")

        # 2. Verifica a presença dos cabeçalhos na resposta real
        if "Content-Security-Policy" in headers:
            status_csp = "ATIVO"
        if "X-Frame-Options" in headers:
            status_xframe = "ATIVO"
        if "X-Content-Type-Options" in headers:
            status_xcontent = "ATIVO"
            
    except Exception:
        # Caso o site bloqueie a requisição ou dê timeout
        servidor_detectado = "Desconhecido ou Protegido (Erro de Conexão)"

    # Monta o bloco de texto estruturado que a IA vai ler e respeitar
    bloco_logs_web = f"""
==================================================
INFORMAÇÕES REAIS DO ALVO ATUAL (CAPTURA DINÂMICA):
Alvo: {alvo}
Servidor Web Detectado: {servidor_detectado}
==================================================

SESSÃO 4: CABEÇALHOS DE SEGURANÇA (OWASP TOP 10)
[STATUS DETECTADO NESTE SITE]:
- Content-Security-Policy: {status_csp}
- X-Frame-Options: {status_xframe}
- X-Content-Type-Options: {status_xcontent}
==================================================
"""
    return bloco_logs_web
