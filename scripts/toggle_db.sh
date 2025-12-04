#!/usr/bin/env bash
# Toggle DB environment for current shell session
# Usage: ./scripts/toggle_db.sh [postgres|sqlite|status]

MODE="$1"
if [ -z "$MODE" ]; then
  MODE=status
fi

case "$MODE" in
  postgres)
    export USE_POSTGRES=1
    echo "Switched to Postgres for this session (USE_POSTGRES=1)."
    ;;
  sqlite)
    unset USE_POSTGRES
    unset DATABASE_URL
    echo "Switched to SQLite for this session (USE_POSTGRES/DATABASE_URL unset)."
    ;;
  status)
    echo "USE_POSTGRES=${USE_POSTGRES:-<not set>}"
    echo "DATABASE_URL=${DATABASE_URL:-<not set>}"
    ;;
  *)
    echo "Usage: $0 [postgres|sqlite|status]"
    exit 1
    ;;
esac
