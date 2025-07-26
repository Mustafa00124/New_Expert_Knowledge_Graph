FROM python:3.10-slim

WORKDIR /code
ENV PORT 8000
EXPOSE 8000

# Install system-level dependencies
RUN apt-get update && \
   apt-get install -y --no-install-recommends \
       libmagic1 \
       libgl1-mesa-glx \
       libreoffice \
       cmake \
       poppler-utils \
       tesseract-ocr && \
   apt-get clean && \
   rm -rf /var/lib/apt/lists/*

# Set LD_LIBRARY_PATH
ENV LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH

# Copy requirements and constraints first (for layer caching)
COPY requirements.txt constraints.txt /code/

# Upgrade pip
RUN pip install --upgrade pip

# Pre-install heavy packages separately to avoid redownloads if others fail
RUN pip install --default-timeout=100 --retries=10 \
    torch==2.3.1+cpu \
    matplotlib==3.10.3 \
    -c constraints.txt

# Install the remaining Python dependencies
RUN pip install --default-timeout=100 --retries=10 \
    -r requirements.txt -c constraints.txt

# Copy rest of the application code
COPY . /code

# Run the backend using gunicorn + uvicorn workers
CMD ["gunicorn", "score:app", "--workers", "8", "--threads", "8", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--timeout", "300"]
