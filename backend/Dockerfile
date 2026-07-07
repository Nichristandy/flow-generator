FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
# Graphviz is often required by networkx/graphviz python packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends graphviz && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create output directory for generated files if it doesn't exist
RUN mkdir -p output

# Expose the application port
EXPOSE 8000

# Run the FastAPI server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
