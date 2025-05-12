FROM python:3.13-alpine

# Set working directory
WORKDIR /api

# Install MySQL client libraries (for connecting to remote MySQL)
RUN apk update && apk add --no-cache \
    mariadb-connector-c-dev \
    gcc \
    musl-dev \
    python3-dev \
    libffi-dev \
    openssl-dev

# Copy your application code
COPY . .

RUN mkdir -p /api/.cache && chmod -R 777 /api

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run your app
CMD ["gunicorn", "-w", "3", "-b", "0.0.0.0", "src.resources_and_models:app"]