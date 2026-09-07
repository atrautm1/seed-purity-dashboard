FROM python:3.11-slim

WORKDIR /app

# Prevent Python from writing pyc files and buffer stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8050

# Run with Gunicorn (4 worker processes, binding to port 8050)
CMD ["gunicorn", "--workers", "4", "--bind", "0.0.0.0:8050", "dashboard:server"]