#!/bin/bash
# Configure CI/CD: managed identity, OIDC federation, GitHub variables, and workflow
set -e

# ── Load Configuration ──────────────────────────────────────────────
if [ ! -f .azure-config ]; then
  echo "ERROR: .azure-config not found. Run provision.sh first."
  exit 1
fi
source .azure-config

# ── Create Managed Identity ─────────────────────────────────────────
echo "Creating managed identity..."
az identity create \
  --name id-news-flash-deploy \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION

# ── Get IDs for Role Assignment ─────────────────────────────────────
echo "Retrieving identity and resource IDs..."
PRINCIPAL_ID=$(az identity show \
  --name id-news-flash-deploy \
  --resource-group $RESOURCE_GROUP \
  --query principalId -o tsv)

ACR_ID=$(az acr show \
  --name $ACR_NAME \
  --resource-group $RESOURCE_GROUP \
  --query id -o tsv)

RG_ID=$(az group show \
  --name $RESOURCE_GROUP \
  --query id -o tsv)

# ── Assign Roles ────────────────────────────────────────────────────
echo "Assigning AcrPush role (waiting for identity to propagate)..."
for i in 1 2 3 4 5; do
  if az role assignment create \
    --assignee $PRINCIPAL_ID \
    --role AcrPush \
    --scope $ACR_ID 2>/dev/null; then
    break
  fi
  echo "  Attempt $i/5 failed, waiting 10s..."
  sleep 10
done

echo "Assigning Contributor role..."
az role assignment create \
  --assignee $PRINCIPAL_ID \
  --role Contributor \
  --scope $RG_ID

# ── Get OIDC Values ─────────────────────────────────────────────────
CLIENT_ID=$(az identity show \
  --name id-news-flash-deploy \
  --resource-group $RESOURCE_GROUP \
  --query clientId -o tsv)

TENANT_ID=$(az account show --query tenantId -o tsv)

SUBSCRIPTION_ID=$(az account show --query id -o tsv)

# ── Ensure GitHub Repository ────────────────────────────────────────
REPO_ROOT=$(git rev-parse --show-toplevel)
GITHUB_REPO=$(cd "$REPO_ROOT" && gh repo view --json nameWithOwner -q .nameWithOwner)

# ── Create Federated Credential ─────────────────────────────────────
echo "Creating OIDC federated credential for $GITHUB_REPO..."
az identity federated-credential create \
  --name github-deploy \
  --identity-name id-news-flash-deploy \
  --resource-group $RESOURCE_GROUP \
  --issuer "https://token.actions.githubusercontent.com" \
  --subject "repo:${GITHUB_REPO}:ref:refs/heads/main" \
  --audiences "api://AzureADTokenExchange"

# ── Set GitHub Variables ─────────────────────────────────────────────
echo "Setting GitHub repository variables..."
gh variable set AZURE_CLIENT_ID --body "$CLIENT_ID"
gh variable set AZURE_TENANT_ID --body "$TENANT_ID"
gh variable set AZURE_SUBSCRIPTION_ID --body "$SUBSCRIPTION_ID"
gh variable set ACR_NAME --body "$ACR_NAME"

# ── Write Workflow File ──────────────────────────────────────────────
echo "Writing .github/workflows/deploy.yml..."
mkdir -p "$REPO_ROOT/.github/workflows"
cat > "$REPO_ROOT/.github/workflows/deploy.yml" << 'WORKFLOW'
name: Build and Deploy

on:
  push:
    branches: [main]
    paths:
      - 'application/**'
      - 'Dockerfile'
      - '.github/workflows/deploy.yml'

permissions:
  id-token: write
  contents: read

env:
  CONTAINER_APP: ca-news-flash
  RESOURCE_GROUP: rg-news-flash

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: azure/login@v2
        with:
          client-id: ${{ vars.AZURE_CLIENT_ID }}
          tenant-id: ${{ vars.AZURE_TENANT_ID }}
          subscription-id: ${{ vars.AZURE_SUBSCRIPTION_ID }}

      - name: Set image tag
        run: echo "IMAGE_TAG=$(echo ${{ github.sha }} | cut -c1-7)" >> $GITHUB_ENV

      - name: Build and push with ACR
        run: |
          az acr build --registry ${{ vars.ACR_NAME }} \
            --image news-flash:${{ env.IMAGE_TAG }} .

      - name: Deploy to Container Apps
        run: |
          ACR_SERVER=$(az acr show --name ${{ vars.ACR_NAME }} --query loginServer -o tsv)
          az containerapp update \
            --name ${{ env.CONTAINER_APP }} \
            --resource-group ${{ env.RESOURCE_GROUP }} \
            --image $ACR_SERVER/news-flash:${{ env.IMAGE_TAG }}
          
          az containerapp ingress update \
            --name ${{ env.CONTAINER_APP }} \
            --resource-group ${{ env.RESOURCE_GROUP }} \
            --target-port 5000

      # Migrations run automatically at container startup via entrypoint.sh

      - name: Health check
        run: |
          FQDN=$(az containerapp show \
            --name ${{ env.CONTAINER_APP }} \
            --resource-group ${{ env.RESOURCE_GROUP }} \
            --query "properties.configuration.ingress.fqdn" -o tsv)
          for i in 1 2 3 4 5; do
            if curl -sf "https://$FQDN/" > /dev/null; then
              echo "Health check passed on attempt $i"
              exit 0
            fi
            echo "Attempt $i/5 failed, waiting 15s..."
            sleep 15
          done
          echo "Health check failed after 5 attempts!"
          exit 1
WORKFLOW

# ── Summary ──────────────────────────────────────────────────────────
echo ""
echo "=== CI/CD Setup Complete ==="
echo "Managed Identity: id-news-flash-deploy"
echo "Federated Repo:   $GITHUB_REPO"
echo "Workflow written to: .github/workflows/deploy.yml"
echo "Push to main to trigger the first deployment."