# --- modulos/inteligencia.py ---
import os
import json
from groq import Groq

def analisar_logs_via_nuvem(log_comple, alvo):
    try:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            return {"erro": "Chave GROQ_API_KEY não configurada no arquivo .env"}
            
        client = Groq(api_key=api_key)
        
        prompt_sistema = (
            "Você é um Auditor Executive de Segurança Cibernética Sênior.\n"
            "Sua tarefa é analisar os logs fornecidos e gerar um relatório técnico detalhado sobre o alvo.\n"
            "REGRAS CRÍTICAS:\n"
            "1. Baseie-se estritamente nos logs fornecidos. Nunca invente portas ou vulnerabilidades que não estejam nos dados.\n"
            "2. Identifique claramente o alvo fornecido e associe todas as descobertas a ele.\n"
            "3. Classifique minuciosamente os riscos encontrados (BAIXO, MÉDIO ou ALTO) e detalhe o impacto técnico de cada um.\n"
            "4. Forneça recomendações de mitigação acionáveis para cada falha encontrada.\n"
            "5. Você deve responder OBRIGATORIAMENTE no formato JSON especificado abaixo, sem qualquer texto antes ou depois."
        )
        
        estrutura_json_esperada = {
            "alvo": "IP ou Dominio analisado",
            "resumo_executivo": "Insira o resumo executivo e contexto de segurança aqui",
            "nivel_risco_geral": "BAIXO, MEDIO ou ALTO",
            "portas_e_servicos": [
                {"porta": "Número", "servico": "Nome do serviço", "versao": "Versão detectada"}
            ],
            "vulnerabilidades_detectadas": [
                {
                    "vulnerabilidade": "Nome da falha",
                    "severidade": "BAIXO, MEDIO ou ALTO",
                    "detalhes_tecnicos": "Descrição detalhada do risco encontrado com base nos logs",
                    "mitigacao": "Recomendações detalhadas para corrigir o problema"
                }
            ]
        }
        
        prompt_sistema_completo = f"{prompt_sistema}\n\nSua resposta deve seguir estritamente este modelo JSON:\n{json.dumps(estrutura_json_esperada, ensure_ascii=False)}"
        
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": prompt_sistema_completo},
                {"role": "user", "content": f"Alvo da análise: {alvo}\n\nLogs coletados:\n{log_comple}"}
            ],
            temperature=0.1,
            max_tokens=3000,
            response_format={"type": "json_object"},
            stream=False
        )
        
        # Converte a string JSON purificada diretamente para um dicionário Python
        relatorio_final = json.loads(completion.choices[0].message.content)
        return relatorio_final
        
    except Exception as e:
        return {"erro": f"Falha ao gerar ou processar o relatório: {str(e)}"}
