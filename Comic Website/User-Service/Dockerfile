FROM python:3.11.14-trixie

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

EXPOSE 5004
CMD ["python", "app.py"]