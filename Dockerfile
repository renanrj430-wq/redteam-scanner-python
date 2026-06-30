FROM python:3.10-slim

# Instala ferramentas do sistema necessárias para o nmap
RUN apt-get update && apt-get install -y nmap iputils-ping && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copia todos os arquivos da pasta atual para dentro do container
COPY . .

# Instala todas as bibliotecas listadas no seu arquivo requirements.txt de uma vez
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8501

ENTRYPOINT ["streamlit", "run", "auditor_web.py", "--server.port=8501", "--server.address=0.0.0.0"]
