FROM python:3.10-slim

# Atualiza listas de pacotes e instala dependências básicas
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    nmap \
    iputils-ping \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copia arquivos
COPY . .

# Atualiza o pip primeiro e instala os requisitos
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

EXPOSE 8501

ENTRYPOINT ["streamlit", "run", "auditor_web.py", "--server.port=8501"]

