#!/bin/bash
# ──────────────────────────────────────────────────────────
# Rollback traffic from Green → Blue (quick rollback)
# ──────────────────────────────────────────────────────────

set -e

NAMESPACE="${1:-default}"

echo "🔄 Rolling back traffic to BLUE deployment..."

# Verify blue deployment is still running
kubectl rollout status deployment/health-app-blue -n $NAMESPACE --timeout=60s

# Switch service selector back to blue
kubectl patch service health-app-service \
    -n $NAMESPACE \
    -p '{"spec":{"selector":{"slot":"blue"}}}'

echo "✅ Traffic rolled back to BLUE successfully!"
echo "   Service: health-app-service → slot=blue"
