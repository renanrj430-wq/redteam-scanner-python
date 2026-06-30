FROM python:3.10-slim

# Atualiza o sistema e instala dependências necessárias
RUN apt-get update && apt-get install -y \
    nmap \
    iputils-ping \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copia os arquivos
COPY . .

# Instala as dependências do requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expõe a porta que o Streamlit usa
EXPOSE 8501

# Comando para iniciar a aplicação
CMD ["streamlit", "run", "auditor_web.py", "--server.port=8501"]
