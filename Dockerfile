# Use the official lightweight Python image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Install necessary system build libraries for compiling packages like ChromaDB or NumPy
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker layer caching
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire workspace into the container
COPY . .

# Expose port (FastAPI defaults. Railway will override this internally with the $PORT env variable)
EXPOSE 8000

# Ensure Python outputs everything straight to the terminal without buffering (great for logs)
ENV PYTHONUNBUFFERED=1

# Start the uvicorn server. 
# We use bash to properly catch the $PORT environment variable injected by Railway. Defaults to 8000 for local testing.
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
