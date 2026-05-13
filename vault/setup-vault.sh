#!/bin/bash
# ──────────────────────────────────────────────────────────
# Vault Setup Script
# Initializes Vault with secrets for the Health Risk Predictor
# ──────────────────────────────────────────────────────────

set -e

VAULT_ADDR="http://127.0.0.1:8200"
VAULT_TOKEN="health-app-token"

export VAULT_ADDR VAULT_TOKEN

echo "🔐 Setting up HashiCorp Vault..."

# Wait for Vault to be ready
until curl -s $VAULT_ADDR/v1/sys/health > /dev/null 2>&1; do
    echo "   Waiting for Vault to start..."
    sleep 2
done

echo "✅ Vault is running at $VAULT_ADDR"

# Helper: run vault commands inside the container
VAULT_EXEC="docker exec -e VAULT_ADDR=http://127.0.0.1:8200 -e VAULT_TOKEN=${VAULT_TOKEN} vault-server"

# Enable KV secrets engine (v2)
$VAULT_EXEC vault secrets enable -path=secret kv-v2 2>/dev/null || echo "   KV engine already enabled"

# Store DockerHub credentials
$VAULT_EXEC vault kv put secret/dockerhub \
    username="p1yush123" \
    password="your-dockerhub-password" \
    registry="https://index.docker.io/v1/"

echo "✅ DockerHub credentials stored at secret/dockerhub"

# Store application secrets
$VAULT_EXEC vault kv put secret/health-app \
    app_secret_key="your-app-secret-key-change-me" \
    db_password="your-db-password" \
    api_key="your-api-key"

echo "✅ Application secrets stored at secret/health-app"

# Store Kubernetes config
$VAULT_EXEC vault kv put secret/kubernetes \
    cluster_name="minikube" \
    namespace="default"

echo "✅ Kubernetes config stored at secret/kubernetes"

# Create policy for Jenkins
$VAULT_EXEC sh -c 'vault policy write jenkins-policy - <<EOF
path "secret/data/dockerhub" {
  capabilities = ["read"]
}
path "secret/data/health-app" {
  capabilities = ["read"]
}
path "secret/data/kubernetes" {
  capabilities = ["read"]
}
EOF'

echo "✅ Jenkins policy created"

# Create token for Jenkins with the policy
JENKINS_TOKEN=$($VAULT_EXEC vault token create -policy=jenkins-policy -period=720h -format=json | python3 -c "import sys,json; print(json.load(sys.stdin)['auth']['client_token'])")

echo ""
echo "══════════════════════════════════════════════════"
echo "  Vault Setup Complete!"
echo "══════════════════════════════════════════════════"
echo "  Vault Address : $VAULT_ADDR"
echo "  Root Token    : $VAULT_TOKEN"
echo "  Jenkins Token : $JENKINS_TOKEN"
echo ""
echo "  Add to Jenkins credentials:"
echo "    Kind: Secret text"
echo "    ID:   vault-token"
echo "    Secret: $JENKINS_TOKEN"
echo "══════════════════════════════════════════════════"
