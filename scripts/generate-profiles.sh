#!/bin/bash
# scripts/generate-profiles.sh
# Reads .env and generates docker compose command with appropriate profiles

set -a
source .env
set +a

PROFILES=""

[[ "$ENABLE_POSTGRES" == "true" ]] && PROFILES="$PROFILES --profile postgres"
[[ "$ENABLE_MONGODB" == "true" ]] && PROFILES="$PROFILES --profile mongodb"
[[ "$ENABLE_NEO4J" == "true" ]] && PROFILES="$PROFILES --profile neo4j"
[[ "$ENABLE_RABBITMQ" == "true" ]] && PROFILES="$PROFILES --profile rabbitmq"
[[ "$ENABLE_CELERY_WORKER" == "true" ]] && PROFILES="$PROFILES --profile celery"
[[ "$ENABLE_FRONTEND" == "true" ]] && PROFILES="$PROFILES --profile frontend"
[[ "$ENABLE_NGINX" == "true" ]] && PROFILES="$PROFILES --profile nginx"
[[ "$ENABLE_LLM_OLLAMA" == "true" ]] && PROFILES="$PROFILES --profile ollama"

# Core services always enabled (no profile needed)
# - backend
# - redis

echo "$PROFILES"
