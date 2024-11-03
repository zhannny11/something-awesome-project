# Dockerfile
FROM python:3.9

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt

# Set the default command to use watchmedo for hot-reloading
CMD ["watchmedo", "auto-restart", "--patterns=*.py", "--recursive", "--", "python", "main.py"]