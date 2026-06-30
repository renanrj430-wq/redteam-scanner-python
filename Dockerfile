FROM python:3.10-slim

# Instala ferramentas do sistema necessárias
RUN apt-get update && apt-get install -y nmap iputils-ping && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copia todos os arquivos do seu repositório para o container
COPY . .

# Instala as dependências a partir do arquivo requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8501

ENTRYPOINT ["streamlit", "run", "auditor_web.py", "--server.port=8501", "--server.address=0.0.0.0"]
