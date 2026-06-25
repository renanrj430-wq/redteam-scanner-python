# --- modulos/inteligencia.py ---
import os
import json
from groq import Groq
# Importa o módulo de captura
from modulos.captura import extrair_contexto_alvo

def analisar_logs_via_nuvem(log_comple, alvo):
    try:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            return {"erro": "Chave GROQ_API_KEY não configurada no arquivo .env"}

        client = Groq(api_key=api_key)

        # 1. PEGA O CONTEXTO REAL DO SITE (Servidor e Cabeçalhos Ativos)
        contexto_web_real = extrair_contexto_alvo(alvo)

        # 2. CONCATENAÇÃO DOS LOGS DINÂMICOS E LOCAIS
        log_final_consolidado = (
            f"{contexto_web_real}\n"
            f"--- LOGS DE REDE E PORTAS DA FERRAMENTA LOCAL ---\n"
            f"{log_comple}"
        )

        # Prompt ajustado com regras de loop estritas
        prompt_sistema = (
            "Você é um Auditor Executivo de Segurança Cibernética Sênior especializado em testes de invasão (Red Team).\n"
            "Sua tarefa é analisar os logs fornecidos e gerar um relatório técnico detalhado sobre o alvo.\n"
            "REGRAS CRÍTICAS:\n"
            "1. Baseie-se estritamente nos logs fornecidos. Nunca invente portas ou vulnerabilidades que não estejam nos dados.\n"
            "2. Identifique claramente o alvo fornecido e associe todas as descobertas a ele.\n"
            "3. Varra os logs de forma abrangente em busca de múltiplos vetores: mapeamento de portas (ex: 21, 22), falhas em bancos de dados (ex: MySQL/3306), falhas em aplicações web e falhas ou ausência de cabeçalhos de segurança (headers).\n"
            "4. PRIORIDADE DE INFRAESTRUTURA: Qualquer porta aberta detectada (ex: 22, 21, 80, 3306) DEVE gerar obrigatoriamente um item correspondente na lista de 'vulnerabilidades_detectadas' detalhando os riscos daquele serviço exposto, além de aparecer em 'portas_e_servicos'.\n"
            "5. Classifique minuciosamente os riscos encontrados (BAIXO, MÉDIO ou ALTO) e detalhe o impacto técnico real e de negócio de cada um.\n"
            "6. IDENTIFICAÇÃO DE TECNOLOGIA: Identifique o servidor web real indicado nas seções de captura dos logs (ex: Vercel, Cloudflare, Nginx, Apache). É PROIBIDO sugerir correções para Apache ou Nginx se o log indicar que o servidor é Vercel ou outro ecossistema. Adapte a mitigação exatamente à tecnologia detectada.\n"
            "7. VALIDAÇÃO DE CABEÇALHOS: Observe atentamente o status dos cabeçalhos nos logs. Se um cabeçalho estiver marcado como 'ATIVO', NÃO o inclua na lista de vulnerabilidades detectadas. Se estiver ausente, reporte.\n"
            "8. Forneça recomendações de mitigação acionáveis. Isso inclui comandos exatos de correção de terminal, caminhos de arquivos de configuração e diretrizes de correção específicas para a falha.\n"
            "9. PROIBIDO LIMITAR A QUANTIDADE: Você deve listar absolutamente todas as falhas encontradas. O array 'vulnerabilidades_detectadas' deve conter tantos objetos quantos forem necessários para cobrir todos os problemas nos logs. Não resuma e não pare em 3 itens.\n"
            "10. Você deve responder OBRIGATORIAMENTE no formato JSON especificado abaixo, sem qualquer texto antes ou depois."
        )

        # Alterado para uma estrutura descritiva que força o loop dinâmico na IA
        estrutura_json_esperada = {
            "alvo": "IP ou Dominio analisado",
            "resumo_executivo": "Resumo técnico contextualizado",
            "nivel_risco_geral": "BAIXO, MEDIO ou ALTO",
            "portas_e_servicos": [
                {
                    "porta": "Número da porta aberta",
                    "servico": "Nome do serviço",
                    "versao": "Versão detectada"
                }
            ],
            "vulnerabilidades_detectadas": [
                "REPETIR_BLOCO_ABAIXO_PARA_CADA_FALHA_OU_PORTA_ABERTA_SEM_LIMITE",
                {
                    "vulnerabilidade": "Nome exato do risco ou cabeçalho ausente ou porta exposta",
                    "severidade": "BAIXO, MEDIO ou ALTO",
                    "detalhes_tecnicos": "Explicação técnica detalhada baseada estritamente nos logs",
                    "mitigacao": "Comandos ou passos exatos de correção específicos para o ambiente atual"
                }
            ]
        }

        prompt_sistema_completo = (
            f"{prompt_sistema}\n\n"
            f"Sua resposta deve ser estritamente um objeto JSON válido seguindo este modelo:\n"
            f"{json.dumps(estrutura_json_esperada, ensure_ascii=False)}"
        )

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": prompt_sistema_completo},
                {"role": "user", "content": f"Alvo da análise: {alvo}\n\nLogs coletados:\n{log_final_consolidado}"}
            ],
            temperature=0.1,
            max_tokens=3000,
            response_format={"type": "json_object"},
            stream=False
        )

        texto_resposta = completion.choices[0].message.content

        try:
            relatorio_final = json.loads(texto_resposta)
            
            # Limpa a string de instrução caso a IA a repita erroneamente no início do array
            vuls = relatorio_final.get("vulnerabilidades_detectadas", [])
            if vuls and isinstance(vuls[0], str):
                relatorio_final["vulnerabilidades_detectadas"] = vuls[1:]
                
            return relatorio_final
        except json.JSONDecodeError:
            return {
                "erro": "A IA não retornou um formato JSON válido.",
                "resposta_bruta": texto_resposta
            }

    except Exception as e:
        return {"erro": f"Falha ao gerar ou processar o relatório: {str(e)}"}
