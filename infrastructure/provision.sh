#!/bin/bash
# Provision all Azure infrastructure for the News Flash application
set -e

# ── Variables ────────────────────────────────────────────────────────
RESOURCE_GROUP="rg-news-flash"
LOCATION="swedencentral"
CAE_NAME="cae-news-flash"
CA_NAME="ca-news-flash"
SQL_ADMIN_USER="sqladmin"
DB_NAME="newsflash"

# Generated values (unique per run)
ACR_NAME="acrnewsflash$(openssl rand -hex 4)"
SQL_SERVER="sql-news-flash-$(openssl rand -hex 4)"
SQL_PASSWORD="$(openssl rand -base64 16)Aa1!"
SECRET_KEY=$(openssl rand -hex 32)

echo "=== News Flash — Azure Provisioning ==="
echo "ACR Name:   $ACR_NAME"
echo "SQL Server: $SQL_SERVER"
echo ""

# ── Resource Group ───────────────────────────────────────────────────
echo "Creating resource group..."
az group create --name $RESOURCE_GROUP --location $LOCATION

# ── Container Registry ──────────────────────────────────────────────
echo "Creating container registry..."
az acr create \
  --name $ACR_NAME \
  --resource-group $RESOURCE_GROUP \
  --sku Basic \
  --admin-enabled true

# ── Container Apps Environment ───────────────────────────────────────
echo "Creating Container Apps Environment (this takes a couple of minutes)..."
az containerapp env create \
  --name $CAE_NAME \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION

# ── Container App (nginx placeholder) ────────────────────────────────
echo "Creating Container App with nginx placeholder..."
az containerapp create \
  --name $CA_NAME \
  --resource-group $RESOURCE_GROUP \
  --environment $CAE_NAME \
  --image nginx:alpine \
  --target-port 80 \
  --ingress external \
  --min-replicas 1 \
  --max-replicas 1

# ── Register ACR Credentials on Container App ───────────────────────
echo "Registering ACR credentials..."
ACR_LOGIN_SERVER=$(az acr show --name $ACR_NAME --query loginServer -o tsv)
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query username -o tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query "passwords[0].value" -o tsv)

az containerapp registry set \
  --name $CA_NAME \
  --resource-group $RESOURCE_GROUP \
  --server $ACR_LOGIN_SERVER \
  --username $ACR_USERNAME \
  --password $ACR_PASSWORD

# ── SQL Server ───────────────────────────────────────────────────────
echo "Creating SQL Server..."
az sql server create \
  --name $SQL_SERVER \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --admin-user $SQL_ADMIN_USER \
  --admin-password "$SQL_PASSWORD"

# ── SQL Server Firewall Rules ───────────────────────────────────────
echo "Configuring firewall rules..."
# Allow Azure services (required for Container Apps)
az sql server firewall-rule create \
  --server $SQL_SERVER \
  --resource-group $RESOURCE_GROUP \
  --name AllowAzureServices \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 0.0.0.0

# Allow all IPs (learning environment only - NOT for production!)
az sql server firewall-rule create \
  --server $SQL_SERVER \
  --resource-group $RESOURCE_GROUP \
  --name AllowAll \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 255.255.255.255

# ── SQL Database ─────────────────────────────────────────────────────
echo "Creating SQL Database..."
az sql db create \
  --name $DB_NAME \
  --server $SQL_SERVER \
  --resource-group $RESOURCE_GROUP \
  --edition Basic \
  --capacity 5

# ── Connection String ────────────────────────────────────────────────
DATABASE_URL="mssql+pyodbc://${SQL_ADMIN_USER}:${SQL_PASSWORD}@${SQL_SERVER}.database.windows.net/${DB_NAME}?driver=ODBC+Driver+18+for+SQL+Server"

# ── Secret Key ───────────────────────────────────────────────────────
echo "Generated SECRET_KEY for Flask session encryption."

# ── Set Environment Variables on Container App ──────────────────────
echo "Configuring environment variables..."
az containerapp update \
  --name $CA_NAME \
  --resource-group $RESOURCE_GROUP \
  --set-env-vars \
    "FLASK_ENV=production" \
    "SECRET_KEY=$SECRET_KEY" \
    "DATABASE_URL=$DATABASE_URL"

# ── Save Configuration ──────────────────────────────────────────────
cat > .azure-config << EOF
RESOURCE_GROUP="$RESOURCE_GROUP"
ACR_NAME="$ACR_NAME"
LOCATION="$LOCATION"
CAE_NAME="$CAE_NAME"
CA_NAME="$CA_NAME"
SQL_SERVER="$SQL_SERVER"
SQL_PASSWORD="$SQL_PASSWORD"
EOF

echo "$DATABASE_URL" > .database-url
chmod 600 .database-url 2>/dev/null || true

echo "$SECRET_KEY" > .secret-key
chmod 600 .secret-key 2>/dev/null || true

# ── Git Ignore ───────────────────────────────────────────────────────
echo "Updating .gitignore..."
for entry in .azure-config .database-url .secret-key; do
  grep -qxF "$entry" .gitignore 2>/dev/null || echo "$entry" >> .gitignore
done

# ── Summary ──────────────────────────────────────────────────────────
echo ""
echo "=== Provisioning Complete ==="
echo "Resource Group: $RESOURCE_GROUP"
echo "ACR Name:       $ACR_NAME"
echo "ACR Login:      $ACR_LOGIN_SERVER"
echo "Container App:  $CA_NAME"
echo "SQL Server:     $SQL_SERVER.database.windows.net"
echo "Database:       $DB_NAME"
echo ""
echo "Config saved to: .azure-config, .database-url, .secret-key"
echo "Added to .gitignore: .azure-config .database-url .secret-key"