#!/bin/bash
# Delete all Azure resources for the News Flash application
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

if [ ! -f "$PROJECT_DIR/.azure-config" ]; then
  echo "ERROR: .azure-config not found. Nothing to delete."
  exit 1
fi

source "$PROJECT_DIR/.azure-config"

echo "This will delete ALL resources in: $RESOURCE_GROUP"
echo ""
read -p "Are you sure? (y/N) " confirm

if [[ "$confirm" == "y" ]]; then
  echo "Deleting resource group $RESOURCE_GROUP..."
  az group delete --name "$RESOURCE_GROUP" --yes --no-wait
  echo "Deletion started (runs in background)."
  rm -f "$PROJECT_DIR/.azure-config" "$PROJECT_DIR/.database-url" "$PROJECT_DIR/.secret-key"
  echo "Local config files removed."
else
  echo "Cancelled."
fi