# Red Team Auditor Pro - V37.0 (Industrial Engine)

Análise automatizada de infraestrutura web, cabeçalhos de segurança e inteligência de ameaças. O **Red Team Auditor Pro** é uma ferramenta de auditoria defensiva e ofensiva desenvolvida em Python com interface gráfica via Streamlit, projetada para analistas de segurança e investigadores em auditorias autorizadas e atividades de Recon (reconhecimento).

---

## 🚀 Funcionalidades e Explicações Técnicas

### 1. Fingerprint de Infraestrutura
* **O que faz:** Identifica as tecnologias ocultas e a infraestrutura que suporta o domínio ou endereço IP do alvo.
* **Explicação técnica:** Realiza a detecção de proxies reversos, provedores de nuvem (como Vercel Edge, AWS, Cloudflare) e identifica o servidor web ativo (Nginx, Apache, etc.).
* **Para que serve:** Permite mapear a superfície de ataque e entender o ambiente de hospedagem antes de avançar para testes intrusivos.

### 2. Análise de Headers de Segurança
* **O que faz:** Efetua uma validação ativa nas respostas HTTP do alvo para verificar a implementação de políticas de segurança essenciais.
* **Explicação técnica:** Analisa se os cabeçalhos de proteção cruciais estão ativos e corretamente configurados:
  * `Content-Security-Policy` (CSP) - Mitiga e previne ataques de XSS (Cross-Site Scripting).
  * `X-Frame-Options` - Protege a aplicação contra ataques de Clickjacking.
  * `X-Content-Type-Options` - Previne o MIME-sniffing de ficheiros maliciosos.
  * `Strict-Transport-Security` (HSTS) - Garante que todas as ligações sejam feitas estritamente via HTTPS.
  * `Permissions-Policy` - Restringe o acesso do navegador a recursos de hardware (câmara, geolocalização, etc.).
* **Para que serve:** Identifica falhas de configuração que deixam os utilizadores expostos a ataques baseados no navegador.

### 3. Auditoria de Cookies
* **O que faz:** Analisa minuciosamente os cookies de sessão emitidos pelo servidor web para garantir que possuem as diretivas de segurança adequadas.
* **Explicação técnica:** Verifica a presença e configuração das flags de segurança essenciais:
  * `HttpOnly`: Impede que scripts maliciosos (via XSS) acedam ou roubem o cookie de sessão.
  * `Secure`: Garante que o cookie seja transmitido exclusivamente através de ligações criptografadas (HTTPS).
  * `SameSite-Policy` (`Lax`, `Strict` ou `None`): Protege a aplicação contra ataques de CSRF (Cross-Site Request Forgery).
* **Para que serve:** Valida se a sessão do utilizador está protegida contra roubo ou falsificação de pedidos.

### 4. Módulo Shodan Intelligence
* **O que faz:** Integra o scanner diretamente com a plataforma Shodan para recolha de inteligência sem interagir diretamente com o alvo (reconhecimento passivo).
* **Explicação técnica:** Utiliza chamadas assíncronas à API do Shodan para levantar portas abertas, serviços ativos, vulnerabilidades conhecidas correlacionadas (CVEs) e dados de OSINT (Open Source Intelligence) expostos.
* **Para que serve:** Permite descobrir vulnerabilidades conhecidas publicamente na internet sem gerar alertas nos sistemas de monitorização internos do alvo.

---
📖 Como Usar (Manual do Utilizador)
​O Red Team Auditor Pro utiliza o Streamlit para fornecer uma interface gráfica moderna, responsiva e inteiramente executada através do seu navegador web.
​Passo 1: Iniciar o Painel Streamlit
​No terminal, certifique-se de que está dentro da pasta do projeto e execute o motor da interface web:

streamlit run auditor_web.py

⚠️ Isenção de Responsabilidade (Disclaimer)
​Esta ferramenta foi desenvolvida estritamente para fins educacionais, testes de penetração legítimos e auditorias de segurança devidamente autorizadas. O uso do Red Team Auditor Pro contra sistemas sem consentimento prévio e por escrito é estritamente ilegal e punível por lei. O desenvolvedor não assume qualquer responsabilidade por eventuais danos ou utilização indevida deste software.

## 🔧 Como Instalar

Siga os passos abaixo no seu terminal para clonar o repositório e preparar o seu ambiente local:
el por lei. O desenvolvedor não assume qualquer responsabilidade por eventuais danos ou utilização indevida deste software.

### 1. Clonar o Repositório e Aceder à Pasta
Abra o terminal e execute o comando para clonar o projeto e entrar no diretório criado:
```bash
git clone [https://github.com/renanrj430-wq/redteam-scanner-python.git](https://github.com/renanrj430-wq/redteam-scanner-python.git)
cd redteam-scanner-python
