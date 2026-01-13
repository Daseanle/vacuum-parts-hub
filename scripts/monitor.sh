#!/bin/bash
# 自动化监控和健康检查脚本
# 用于 24/7 监控网站运行状态

set -e

# 配置
SITE_URL="https://vacuumpartshub.com"
HEALTH_CHECK_ENDPOINT="/api/health"
LOG_FILE="./logs/monitor-$(date +%Y%m%d).log"
ALERT_EMAIL="${ALERT_EMAIL:-admin@vacuumpartshub.com}"
SLACK_WEBHOOK_URL="${SLACK_WEBHOOK_URL:-}"

# 创建日志目录
mkdir -p ./logs

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 日志函数
log() {
  local level=$1
  shift
  local message="$@"
  local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
  echo "[$timestamp] [$level] $message" | tee -a "$LOG_FILE"
}

# 发送告警函数
send_alert() {
  local status=$1
  local message=$2

  log "ALERT" "状态: $status, 消息: $message"

  # 发送邮件告警（如果配置了）
  if [ -n "$ALERT_EMAIL" ]; then
    echo "$message" | mail -s "[$status] Vacuum Parts Hub 告警" "$ALERT_EMAIL" 2>/dev/null || true
  fi

  # 发送 Slack 告警（如果配置了）
  if [ -n "$SLACK_WEBHOOK_URL" ]; then
    curl -s -X POST "$SLACK_WEBHOOK_URL" \
      -H 'Content-Type: application/json' \
      -d "{\"text\": \"[$status] $message\"}" \
      2>/dev/null || true
  fi
}

# HTTP 状态码检查
check_http_status() {
  local url=$1
  local expected_code=${2:-200}

  local response=$(curl -s -o /dev/null -w "%{http_code}" "$url" --max-time 10)

  if [ "$response" -eq "$expected_code" ]; then
    log "INFO" "✓ HTTP 状态检查通过: $url (HTTP $response)"
    return 0
  else
    log "ERROR" "✗ HTTP 状态检查失败: $url (预期: $expected_code, 实际: $response)"
    send_alert "CRITICAL" "网站无法访问: $url 返回 HTTP $response"
    return 1
  fi
}

# 响应时间检查
check_response_time() {
  local url=$1
  local max_time=${2:-3}

  local time=$(curl -s -o /dev/null -w "%{time_total}" "$url" --max-time 10)

  # 使用 bc 进行浮点数比较
  if (( $(echo "$time <= $max_time" | bc -l) )); then
    log "INFO" "✓ 响应时间检查通过: ${time}s (上限: ${max_time}s)"
    return 0
  else
    log "WARN" "⚠ 响应时间过长: ${time}s (上限: ${max_time}s)"
    send_alert "WARNING" "网站响应时间过长: ${time}s"
    return 1
  fi
}

# SSL 证书检查
check_ssl_certificate() {
  local domain=$1
  local days_threshold=30

  local expiry_date=$(echo | openssl s_client -servername "$domain" -connect "$domain:443" 2>/dev/null | openssl x509 -noout -enddate | cut -d= -f2)

  if [ -z "$expiry_date" ]; then
    log "ERROR" "✗ 无法获取 SSL 证书信息"
    return 1
  fi

  local expiry_epoch=$(date -d "$expiry_date" +%s)
  local current_epoch=$(date +%s)
  local days_until_expiry=$(( ($expiry_epoch - $current_epoch) / 86400 ))

  if [ $days_until_expiry -lt $days_threshold ]; then
    log "WARN" "⚠ SSL 证书即将过期: ${days_until_expiry} 天后过期"
    send_alert "WARNING" "SSL 证书将在 ${days_until_expiry} 天后过期"
    return 1
  else
    log "INFO" "✓ SSL 证书检查通过: ${days_until_expiry} 天后过期"
    return 0
  fi
}

# DNS 检查
check_dns() {
  local domain=$1

  if nslookup "$domain" >/dev/null 2>&1; then
    local ip=$(nslookup "$domain" | grep -A1 "Name:" | tail -n1 | awk '{print $2}')
    log "INFO" "✓ DNS 检查通过: $domain 解析到 $ip"
    return 0
  else
    log "ERROR" "✗ DNS 检查失败: $domain 无法解析"
    send_alert "CRITICAL" "DNS 解析失败: $domain"
    return 1
  fi
}

# 关键词检查（确保页面内容正确）
check_content() {
  local url=$1
  local keyword=$2

  local content=$(curl -s "$url" --max-time 10)

  if echo "$content" | grep -qi "$keyword"; then
    log "INFO" "✓ 内容检查通过: 找到关键词 '$keyword'"
    return 0
  else
    log "ERROR" "✗ 内容检查失败: 未找到关键词 '$keyword'"
    send_alert "CRITICAL" "页面内容异常: 未找到关键词 '$keyword'"
    return 1
  fi
}

# 主监控函数
run_monitoring() {
  log "INFO" "=========================================="
  log "INFO" "开始监控检查"
  log "INFO" "=========================================="

  local all_passed=true

  # 1. DNS 检查
  check_dns "$(echo "$SITE_URL" | sed -e 's|^[^/]*//||' -e 's|/.*$||')" || all_passed=false

  # 2. SSL 证书检查
  check_ssl_certificate "$(echo "$SITE_URL" | sed -e 's|^[^/]*//||' -e 's|/.*$||')" || all_passed=false

  # 3. HTTP 状态检查
  check_http_status "$SITE_URL" || all_passed=false

  # 4. 响应时间检查
  check_response_time "$SITE_URL" || all_passed=false

  # 5. 内容检查
  check_content "$SITE_URL" "VacuumPartsHub" || all_passed=false

  log "INFO" "=========================================="
  if [ "$all_passed" = true ]; then
    log "INFO" "✅ 所有监控检查通过"
  else
    log "ERROR" "❌ 部分监控检查失败"
  fi
  log "INFO" "=========================================="
}

# 执行监控
if [ "$1" = "--daemon" ]; then
  log "INFO" "启动守护进程模式"
  while true; do
    run_monitoring
    log "INFO" "等待 5 分钟后进行下一次检查..."
    sleep 300
  done
else
  run_monitoring
fi
