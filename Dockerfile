FROM python:3.12-slim

WORKDIR /app

RUN pip install streamlit streamlit-authenticator pandas numpy

COPY . .

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]