FROM python:3.10-slim
RUN apt-get update && apt-get install -y nmap iputils-ping && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir streamlit requests shodan python-dotenv colorama hashid
EXPOSE 8501
ENTRYPOINT ["streamlit", "run", "auditor_web.py", "--server.port=8501", "--server.address=0.0.0.0"]

