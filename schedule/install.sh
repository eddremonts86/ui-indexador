#!/usr/bin/env bash
#
# Run ui-indexador as local macOS services (launchd, per user):
#   ui-indexador.api      server.py on 127.0.0.1:3040, kept alive      (the HTTP API and the landing page)
#   ui-indexador.mcp      mcp_server.py --http on 127.0.0.1:3041/mcp   (for MCP clients that connect by URL)
#   ui-indexador.refresh  refresh.sh every day at 11:30                (notifies on failure, logs 14 days)
#
#   bash schedule/install.sh               # install + load all three
#   bash schedule/install.sh --run-now     # also start a refresh now, through launchd (checks PATH and env)
#   bash schedule/install.sh --status
#   bash schedule/install.sh --uninstall
#
# Env passed to the services: UI_INDEXER_OLLAMA (default http://localhost:11434), UI_INDEXER_PYTHON
# (default .venv/bin/python). Linux: run the same three commands with systemd or cron.

set -euo pipefail

APP="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DOMAIN="gui/$(id -u)"
AGENTS="$HOME/Library/LaunchAgents"
PY="${UI_INDEXER_PYTHON:-$APP/.venv/bin/python}"
OLLAMA="${UI_INDEXER_OLLAMA:-http://localhost:11434}"
LABELS=(ui-indexador.api ui-indexador.mcp ui-indexador.refresh)

log() { printf '[ui-indexador] %s\n' "$*"; }
loaded() { launchctl print "$DOMAIN/$1" >/dev/null 2>&1; }
x() { sed -e 's/&/\&amp;/g' -e 's/</\&lt;/g' -e 's/>/\&gt;/g' <<<"$1"; }

plist() {  # label, then either "keepalive" or "daily", then the shell command
  local label=$1 mode=$2 cmd=$3 when
  if [ "$mode" = keepalive ]; then
    when="<key>RunAtLoad</key><true/><key>KeepAlive</key><true/>"
  else
    when="<key>StartCalendarInterval</key><dict><key>Hour</key><integer>11</integer><key>Minute</key><integer>30</integer></dict>"
  fi
  cat <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>$label</string>
  <key>ProgramArguments</key><array><string>/bin/bash</string><string>-c</string><string>$(x "$cmd")</string></array>
  <key>EnvironmentVariables</key><dict>
    <key>PATH</key><string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
    <key>HOME</key><string>$HOME</string>
    <key>UI_INDEXER_OLLAMA</key><string>$OLLAMA</string>
    <key>UI_INDEXER_PYTHON</key><string>$PY</string>
  </dict>
  $when
  <key>WorkingDirectory</key><string>$APP</string>
  <key>LowPriorityIO</key><true/>
  <key>StandardOutPath</key><string>$APP/logs/$label.log</string>
  <key>StandardErrorPath</key><string>$APP/logs/$label.log</string>
</dict></plist>
PLIST
}

case "${1:-install}" in
  --status)
    for l in "${LABELS[@]}"; do log "$l: $(loaded "$l" && echo loaded || echo NOT loaded)"; done
    curl -sf -m 3 http://127.0.0.1:3040/health >/dev/null && log "api answers on :3040" || log "api not answering on :3040"
    f="$(ls -t "$APP"/logs/refresh-*.log 2>/dev/null | head -1 || true)"
    [ -n "$f" ] && { log "last refresh: $(basename "$f")"; tail -2 "$f" | sed 's/^/[ui-indexador]   /'; } || log "last refresh: never"
    exit 0 ;;
  --uninstall)
    for l in "${LABELS[@]}"; do launchctl bootout "$DOMAIN/$l" 2>/dev/null || true; rm -f "$AGENTS/$l.plist"; done
    log "removed ${LABELS[*]}"; exit 0 ;;
  install|--run-now) ;;
  *) echo "unknown flag: $1 (try --run-now, --status or --uninstall)" >&2; exit 2 ;;
esac

[ -x "$PY" ] || { echo "no Python at $PY: python3 -m venv .venv && .venv/bin/pip install -r requirements.txt" >&2; exit 1; }
mkdir -p "$APP/logs" "$AGENTS"
plist ui-indexador.api keepalive "exec \"$PY\" server.py" > "$AGENTS/ui-indexador.api.plist"
plist ui-indexador.mcp keepalive "exec \"$PY\" mcp_server.py --http" > "$AGENTS/ui-indexador.mcp.plist"
plist ui-indexador.refresh daily "log=\"$APP/logs/refresh-\$(date +%Y-%m-%d-%H%M%S).log\"; bash refresh.sh > \"\$log\" 2>&1 || osascript -e 'display notification \"refresh failed, see logs/\" with title \"ui-indexador\"'; find logs -name 'refresh-*.log' -mtime +14 -delete" > "$AGENTS/ui-indexador.refresh.plist"

for l in "${LABELS[@]}"; do
  plutil -lint "$AGENTS/$l.plist" >/dev/null
  launchctl bootout "$DOMAIN/$l" 2>/dev/null || true
  for _ in $(seq 1 10); do loaded "$l" || break; sleep 1; done
  for attempt in 1 2 3; do  # bootstrap right after bootout can fail with "5: I/O error"
    launchctl bootstrap "$DOMAIN" "$AGENTS/$l.plist" 2>/dev/null && break
    [ "$attempt" = 3 ] && { echo "launchctl bootstrap failed for $l" >&2; exit 1; }
    sleep 2
  done
  log "loaded $l"
done

if [ "${1:-}" = "--run-now" ]; then
  launchctl kickstart "$DOMAIN/ui-indexador.refresh"
  log "refresh started; follow it: tail -f \$(ls -t $APP/logs/refresh-*.log | head -1)"
fi
