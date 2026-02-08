# Flask with Azure SQL Database
FROM python:3.11-slim

# Install ODBC Driver 18 for Azure SQL Database
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl gnupg2 unixodbc \
    && curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg \
    && curl -fsSL https://packages.microsoft.com/config/debian/12/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y --no-install-recommends msodbcsql18 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first for layer caching
COPY application/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY application/ .

EXPOSE 5000

# Run migrations at startup, then start gunicorn
CMD ["bash", "entrypoint.sh"]# Trigger build
echo "# Restart trigger" >> Dockerfile