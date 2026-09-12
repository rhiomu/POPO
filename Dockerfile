FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=7860 \
    HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# Create non-root user (Hugging Face Spaces requirement)
RUN useradd -m -u 1000 user

WORKDIR /home/user/app

# Install dependencies first for better caching
COPY --chown=user:user requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy application files
COPY --chown=user:user . .

# Hugging Face Spaces standard port
EXPOSE 7860

# Switch to non-root user
USER user

# Start server
CMD ["uvicorn", "src.po_auditor.app:app", "--host", "0.0.0.0", "--port", "7860"]
