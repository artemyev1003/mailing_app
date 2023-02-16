FROM python:latest

# This prevents Python from writing out pyc files
ENV PYTHONDONTWRITEBYTECODE=1
# This keeps Python from buffering stdin/stdout
ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY . /app

RUN pip install -r requirements.txt

CMD ["python", "notification_sender.py"]
