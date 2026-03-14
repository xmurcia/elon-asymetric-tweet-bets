#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"

echo "[smoke] waiting for backend at $BASE_URL/health"

# basic retry loop
for i in {1..30}; do
  if curl -fsS "$BASE_URL/health" >/dev/null; then
    echo "[smoke] backend is up"
    break
  fi
  sleep 1
  if [ "$i" -eq 30 ]; then
    echo "[smoke] backend did not become ready" >&2
    exit 1
  fi
done

echo "[smoke] GET /health"
curl -fsS "$BASE_URL/health" | tee /tmp/health.json

echo "[smoke] GET /metrics"
curl -fsS "$BASE_URL/metrics" | tee /tmp/metrics.json

# super-light assertions (no extra deps)
if ! grep -q '"status"[[:space:]]*:[[:space:]]*"ok"' /tmp/health.json; then
  echo "[smoke] unexpected /health response" >&2
  cat /tmp/health.json >&2
  exit 1
fi

if ! grep -q '"uptime_seconds"' /tmp/metrics.json; then
  echo "[smoke] /metrics missing uptime_seconds" >&2
  cat /tmp/metrics.json >&2
  exit 1
fi

if ! grep -q '"total_requests"' /tmp/metrics.json; then
  echo "[smoke] /metrics missing total_requests" >&2
  cat /tmp/metrics.json >&2
  exit 1
fi

echo "[smoke] ok"
