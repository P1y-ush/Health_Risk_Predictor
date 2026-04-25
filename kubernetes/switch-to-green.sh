#!/bin/bash
# ──────────────────────────────────────────────────────────
# Switch traffic from Blue → Green (zero-downtime deployment)
# ──────────────────────────────────────────────────────────

set -e

NAMESPACE="${1:-default}"

echo "🔄 Switching traffic to GREEN deployment..."

# Verify green deployment is ready
kubectl rollout status deployment/health-app-green -n $NAMESPACE --timeout=60s

# Switch service selector to green
kubectl patch service health-app-service \
    -n $NAMESPACE \
    -p '{"spec":{"selector":{"slot":"green"}}}'

echo "✅ Traffic switched to GREEN successfully!"
echo "   Service: health-app-service → slot=green"
echo ""
echo "To rollback to blue, run: ./rollback-to-blue.sh"
