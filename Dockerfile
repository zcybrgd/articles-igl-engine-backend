FROM python:3.10
WORKDIR /app


COPY requirements.txt .
RUN pip install -r requirements.txt


COPY . .

# Expose port
EXPOSE 8000

# entrypoint to run the django.sh file
ENTRYPOINT ["/app/bash.sh"]
