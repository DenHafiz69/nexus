FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for psycopg2 if not using the binary version
# RUN apt-get update && apt-get install -y libpq-dev gcc

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000