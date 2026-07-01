# --- modulos/inteligencia.py ---
import os
import json
from groq import Groq
from modulos.captura import extrair_contexto_alvo

def analisar_logs_via_nuvem(log_comple, alvo):
    try:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            return {"erro": "Chave GROQ_API_KEY não configurada"}

        client = Groq(api_key=api_key)
        contexto_web_real = extrair_contexto_alvo(alvo)

        log_final_consolidado = (
            f"{contexto_web_real}\n"
            f"--- LOGS DE REDE E PORTAS DA FERRAMENTA LOCAL ---\n"
            f"{log_comple}"
        )

        prompt_sistema = (
            "Você é um Auditor Executivo de Segurança Sênior. Sua tarefa é analisar os logs e gerar um relatório técnico.\n"
            "REGRAS CRÍTICAS:\n"
            "1. Baseie-se estritamente nos logs fornecidos. Proibido inventar dados.\n"
            "2. Identifique o alvo e associe as descobertas a ele.\n"
            "3. Analise todos os vetores: SSH (22), FTP (21), Bancos de Dados (3306), Web e Cabeçalhos.\n"
            "4. PRIORIDADE DE INFRAESTRUTURA: Portas como 22, 21 e 3306 SÃO RISCO ALTO. Devem ser detalhadas individualmente.\n"
            "5. Classifique riscos (BAIXO, MÉDIO, ALTO) e detalhe o impacto técnico/negócio.\n"
            "6. IDENTIFICAÇÃO DE TECNOLOGIA: Adapte a mitigação exatamente à tecnologia detectada (Vercel, Cloudflare, Nginx, Apache).\n"
            "7. VALIDAÇÃO: Se o cabeçalho estiver marcado como 'ATIVO', não reporte. Reporte apenas se ausente.\n"
            "8. MITIGAÇÃO: Forneça comandos exatos de terminal/configuração. NUNCA use 'N/A'.\n"
            "9. EXAUSTIVIDADE: Liste absolutamente TODAS as falhas. Proibido resumir ou limitar o número de itens.\n"
            "10. Responda OBRIGATORIAMENTE em JSON puro, sem textos adicionais."
        )

        estrutura_json_esperada = {
            "alvo": "string",
            "resumo_executivo": "string",
            "nivel_risco_geral": "string",
            "portas_e_servicos": [
                {"porta": "int", "servico": "string", "versao": "string"}
            ],
            "vulnerabilidades_detectadas": [
                {
                    "vulnerabilidade": "string",
                    "severidade": "string",
                    "detalhes_tecnicos": "string",
                    "mitigacao": "string"
                }
            ]
        }

            completion = client.chat.completions.create(
            model="openai/gpt-oss-120b"
            messages=[
                {"role": "system", "content": f"{prompt_sistema}\n\nResponda usando estritamente este esquema JSON: {json.dumps(estrutura_json_esperada, ensure_ascii=False)}"},
                {"role": "user", "content": f"Alvo: {alvo}\n\nLogs coletados:\n{log_final_consolidado}"}
            ],
            temperature=0.1,
            max_tokens=6000,
            response_format={"type": "json_object"}
        )

        return json.loads(completion.choices[0].message.content)

    except Exception as e:
        return {"erro": f"Falha ao processar auditoria: {str(e)}"}
