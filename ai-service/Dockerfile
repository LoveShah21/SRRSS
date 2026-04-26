# Dockerfile for Hugging Face Spaces (Docker Space)
FROM python:3.11-slim

# Set up a new user named "user" with user ID 1000
# Hugging Face Spaces require the app to run as a non-root user
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

WORKDIR /app

# Install dependencies
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m spacy download en_core_web_sm

# Copy the rest of the application
COPY --chown=user . .

# Hugging Face Spaces expects the app to run on port 7860
EXPOSE 7860

# Run FastAPI using uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
