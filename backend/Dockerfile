# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Hugging Face Spaces requires running on a specific port and user namespace
ENV PORT=7860
EXPOSE ${PORT}

# Set up a new user named "user" with user ID 1000
RUN useradd -m -u 1000 user

# Install system dependencies (required for LightGBM or other ML packages if needed)
RUN apt-get update && apt-get install -y \
    build-essential \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Switch to the "user" user
USER user

# Set home to the user's home directory
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# Set work directory
WORKDIR $HOME/app

# Copy the requirements file into the container, changing ownership to user
COPY --chown=user requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY --chown=user . .

# Run the Fast API application utilizing Uvicorn binding to the required port
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]

