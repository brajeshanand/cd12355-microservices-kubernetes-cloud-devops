# Use a lightweight Python runtime as base image
FROM python:3.9-slim

# Set working directory inside the container
WORKDIR /app

# Copy and install dependencies
COPY ./analytics/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r /app/requirements.txt

# Copy application files
COPY ./analytics /app

# Expose the application port
EXPOSE 5153

# Use environment variables from runtime (avoid hardcoding secrets)
ENV APP_PORT=5153

# Run the Flask app with Gunicorn for better performance
#CMD ["gunicorn", "--bind", "0.0.0.0:5153", "app:app"]
CMD ["python", "app.py"]

