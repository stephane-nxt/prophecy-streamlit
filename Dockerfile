FROM python:3.12-slim

WORKDIR /app

RUN pip install streamlit streamlit-authenticator pandas numpy boto3 pyarrow plotly

COPY . .

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]