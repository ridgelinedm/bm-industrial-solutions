#!/usr/bin/env bash
# Tiny ClickUp API wrapper for the ticket workflows.
#
#   clickup.sh comment <task_id> <text>     post a comment (notifies watchers)
#   clickup.sh status  <task_id> <status>   move the task to a status
#
# Needs CLICKUP_API_TOKEN. Without it the call is skipped with a warning, so
# the GitHub side still works before ClickUp is wired up.
set -euo pipefail

cmd="${1:?usage: clickup.sh comment|status <task_id> <value>}"
task="${2:?task id required}"
value="${3:?value required}"

if [[ -z "${CLICKUP_API_TOKEN:-}" ]]; then
  echo "::warning::CLICKUP_API_TOKEN is not set; skipped ClickUp $cmd on $task"
  exit 0
fi

api="https://api.clickup.com/api/v2/task/$task"

case "$cmd" in
  comment)
    body=$(jq -n --arg t "$value" '{comment_text: $t, notify_all: true}')
    curl -fsS -X POST "$api/comment" \
      -H "Authorization: $CLICKUP_API_TOKEN" -H "Content-Type: application/json" \
      -d "$body" >/dev/null
    ;;
  status)
    body=$(jq -n --arg s "$value" '{status: $s}')
    curl -fsS -X PUT "$api" \
      -H "Authorization: $CLICKUP_API_TOKEN" -H "Content-Type: application/json" \
      -d "$body" >/dev/null
    ;;
  *)
    echo "unknown command: $cmd" >&2
    exit 2
    ;;
esac
