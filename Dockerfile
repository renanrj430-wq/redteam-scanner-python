FROM python:3.10-slim

# Instala dependências de sistema essenciais
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    nmap \
    iputils-ping \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Atualiza o pip primeiro e depois instala os requisitos
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

ENTRYPOINT ["streamlit", "run", "auditor_web.py", "--server.port=8501"]

