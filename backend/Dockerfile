FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for audio processing if needed (e.g. portaudio)
# For now, we just need basic build tools
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

ENV GRPC_ENABLE_FORK_SUPPORT=0

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
