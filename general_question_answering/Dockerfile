# Use python base image
# For Apple Silicon (ARM):
    #FROM python:3.9-slim
    # For AMD64 (Intel/AMD), comment above and uncomment below:
    FROM amd64/python:3.9-slim
    
    # Set working directory
    WORKDIR /app
    
    # Install system dependencies
    RUN apt-get update && apt-get install -y \
        build-essential \
        && rm -rf /var/lib/apt/lists/*
    
    # Copy requirements first to leverage Docker cache
    COPY requirements.txt .
    
    # Install Python dependencies
    RUN pip install --no-cache-dir -r requirements.txt
    COPY . .
    RUN pip install --no-cache-dir gradio
    EXPOSE 7860
    ENV GRADIO_SERVER_NAME="0.0.0.0"
    
    # Copy application code
    COPY . .
    
    # Create logs directory
    RUN mkdir -p logs
    
    # Create non-root user
    RUN useradd -m appuser && chown -R appuser:appuser /app
    USER appuser
    
    # Make sure stdin and tty are available for interactive use
    ENV PYTHONUNBUFFERED=1
    
    # Command to run the application
    # Note: We'll override this in docker-compose for interactive use
    CMD ["python", "main.py"]
