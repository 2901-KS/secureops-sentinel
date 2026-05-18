#!/bin/bash

PUSHGATEWAY_URL="http://localhost:9091"
LOG_FILE="security.log"

generate_log_entry() {
  local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
  local events=("FAILED_LOGIN" "RATE_LIMIT" "BLOCKED_IP" "SUSPICIOUS_SCAN" "AUTH_SUCCESS")
  local ips=("192.168.1.10" "10.0.0.55" "172.16.0.8" "203.0.113.42" "198.51.100.7")
  local event=${events[$RANDOM % ${#events[@]}]}
  local ip=${ips[$RANDOM % ${#ips[@]}]}
  echo "$timestamp | $event | ip=$ip | user=admin"
}

parse_and_push() {
  local failed_logins=0
  local rate_limits=0
  local blocked_ips=0
  local suspicious_scans=0

  while IFS= read -r line; do
    [[ "$line" == *"FAILED_LOGIN"* ]]    && ((failed_logins++))
    [[ "$line" == *"RATE_LIMIT"* ]]      && ((rate_limits++))
    [[ "$line" == *"BLOCKED_IP"* ]]      && ((blocked_ips++))
    [[ "$line" == *"SUSPICIOUS_SCAN"* ]] && ((suspicious_scans++))
  done < "$LOG_FILE"

  cat <<EOF | curl -s --data-binary @- "$PUSHGATEWAY_URL/metrics/job/log_parser/instance/bash"
# HELP log_failed_logins_total Failed logins parsed from log file
# TYPE log_failed_logins_total counter
log_failed_logins_total $failed_logins
# HELP log_rate_limit_total Rate limit events parsed from log file
# TYPE log_rate_limit_total counter
log_rate_limit_total $rate_limits
# HELP log_blocked_ips_total Blocked IP events parsed from log file
# TYPE log_blocked_ips_total counter
log_blocked_ips_total $blocked_ips
# HELP log_suspicious_scans_total Suspicious scan events parsed from log file
# TYPE log_suspicious_scans_total counter
log_suspicious_scans_total $suspicious_scans
EOF

  echo "[$(date '+%H:%M:%S')] Pushed — failed_logins=$failed_logins | rate_limits=$rate_limits | blocked_ips=$blocked_ips | scans=$suspicious_scans"
}

echo "Starting log parser — pushing to Pushgateway every 30s"
echo "Log file: $LOG_FILE"

while true; do
  for i in $(seq 1 $((RANDOM % 5 + 1))); do
    generate_log_entry >> "$LOG_FILE"
  done
  parse_and_push
  sleep 30
done
