# --- modulos/inteligencia.py ---
import os
import json
import streamlit as st
from groq import Groq
from modulos.captura import extrair_contexto_alvo

def analisar_logs_via_nuvem(log_comple, alvo):
    try:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            return {"erro": "Chave API não configurada."}

        client = Groq(api_key=api_key)
        contexto_web_real = extrair_contexto_alvo(alvo)
        
        log_final = f"CONTEXTO DO ALVO:\n{contexto_web_real}\n\nLOGS TÉCNICOS:\n{log_comple}"

        prompt_sistema = (
            "Você é um Auditor Executivo de Segurança Sênior. Siga rigorosamente as 10 regras abaixo:\n"
            "1. Baseie-se estritamente nos logs fornecidos. Proibido inventar dados.\n"
            "2. Identifique o alvo e associe as descobertas a ele.\n"
            "3. Analise todos os vetores: SSH (22), FTP (21), Bancos de Dados (3306), Web e Cabeçalhos.\n"
            "4. PRIORIDADE DE INFRAESTRUTURA: Portas 22, 21 e 3306 SÃO RISCO ALTO. Detalhe cada uma.\n"
            "5. Classifique riscos (BAIXO, MÉDIO, ALTO) e detalhe o impacto.\n"
            "6. TECNOLOGIA: Adapte a mitigação exatamente à tecnologia detectada (Vercel, Nginx, Apache, etc).\n"
            "7. VALIDAÇÃO: Se o cabeçalho estiver 'ATIVO' no contexto, não reporte como falta.\n"
            "8. MITIGAÇÃO: Forneça comandos exatos de terminal/configuração. NUNCA use 'N/A'.\n"
            "9. EXAUSTIVIDADE: Liste TODAS as falhas detectadas. Não resuma.\n"
            "10. Responda OBRIGATORIAMENTE em JSON puro. Estrutura: 'alvo', 'resumo_executivo', 'nivel_risco_geral', 'vulnerabilidades_detectadas'.\n"
            "vulnerabilidades_detectadas deve ser uma lista com: 'vulnerabilidade', 'severidade', 'detalhes_tecnicos', 'mitigacao'."
        )

        completion = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": prompt_sistema},
                {"role": "user", "content": f"Alvo: {alvo}\nLogs coletados: {log_final}"}
            ],
            temperature=0.0,
            max_tokens=6000,
            response_format={"type": "json_object"}
        )

        conteudo = completion.choices[0].message.content
        return json.loads(conteudo)

    except Exception as e:
        # Fallback para evitar falhas silenciosas
        return {
            "alvo": alvo,
            "resumo_executivo": f"Erro interno de análise: {str(e)}",
            "nivel_risco_geral": "Indeterminado",
            "vulnerabilidades_detectadas": []
        }
