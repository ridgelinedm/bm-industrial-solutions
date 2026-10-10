#!/usr/bin/env bash
# Tiny ClickUp API wrapper for the ticket workflows.
#
#   clickup.sh get     <task_id>            print the task as JSON
#   clickup.sh comment <task_id> <text>     post a comment (notifies watchers)
#   clickup.sh status  <task_id> <status>   move the task to a status
#   clickup.sh assign  <task_id> <user_id>  add an assignee (no-op if already on it)
#
# Needs CLICKUP_API_TOKEN. Without it, writes are skipped with a warning so the
# GitHub side still works before ClickUp is wired up; `get` fails.
set -euo pipefail

cmd="${1:?usage: clickup.sh get|comment|status|assign <task_id> [value]}"
task="${2:?task id required}"

if [[ -z "${CLICKUP_API_TOKEN:-}" ]]; then
  if [[ "$cmd" == get ]]; then
    echo "CLICKUP_API_TOKEN is not set" >&2
    exit 1
  fi
  echo "::warning::CLICKUP_API_TOKEN is not set; skipped ClickUp $cmd on $task"
  exit 0
fi

api="https://api.clickup.com/api/v2/task/$task"

call() {
  local method="$1" url="$2" body="${3:-}"
  if [[ -n "$body" ]]; then
    curl -fsS -X "$method" "$url" \
      -H "Authorization: $CLICKUP_API_TOKEN" -H "Content-Type: application/json" \
      -d "$body"
  else
    curl -fsS -X "$method" "$url" -H "Authorization: $CLICKUP_API_TOKEN"
  fi
}

case "$cmd" in
  get)
    call GET "$api?include_markdown_description=true"
    ;;
  comment)
    call POST "$api/comment" "$(jq -n --arg t "${3:?text required}" '{comment_text: $t, notify_all: true}')" >/dev/null
    ;;
  status)
    call PUT "$api" "$(jq -n --arg s "${3:?status required}" '{status: $s}')" >/dev/null
    ;;
  assign)
    call PUT "$api" "$(jq -n --argjson u "${3:?user id required}" '{assignees: {add: [$u]}}')" >/dev/null
    ;;
  *)
    echo "unknown command: $cmd" >&2
    exit 2
    ;;
esac
