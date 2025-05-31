FROM python:3.9-slim-buster

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . .

EXPOSE 8001

CMD ["uvicorn", "backend_app.main:app", "--host", "0.0.0.0", "--port", "8001"]