# SecureOps Sentinel 🔐

> Security Infrastructure Observability Stack  
> Real-time threat monitoring using Prometheus, Grafana, and AWS CloudWatch

---

## Architecture

```
FastAPI /metrics  ──►  Prometheus (scrape every 15s)  ──►  Grafana dashboards
     │                        │                                    │
     │                  alert_rules.yml                     8 security panels
     │                        │                              alert rules
     ▼                        ▼
Simulation endpoints    AlertManager (Phase 2)
/simulate/brute-force
/simulate/login-spike
/simulate/rate-limit
```

## Stack

| Component | Purpose |
|-----------|---------|
| FastAPI | Security event simulator + `/metrics` endpoint |
| Prometheus | Scrapes and stores time-series metrics (15s interval) |
| Grafana | Dashboards, visualisations, alert rules |
| Docker Compose | Runs the full stack locally |

## Metrics exposed

| Metric | Type | Description |
|--------|------|-------------|
| `security_failed_login_total` | Counter | Failed login attempts by IP and username |
| `security_brute_force_attempts_total` | Counter | Brute-force events detected |
| `security_suspicious_ip_count` | Gauge | Live count of flagged IPs |
| `security_rate_limit_violations_total` | Counter | API rate limit breaches by endpoint |
| `security_active_sessions_total` | Gauge | Live authenticated session count |
| `security_auth_latency_seconds` | Histogram | Auth request latency (p50/p95/p99) |
| `security_blocked_requests_total` | Counter | Blocked requests by block reason |
| `security_alert_events_total` | Counter | Security alerts by severity |

---

## Quick start

**Prerequisites:** Docker Desktop running on WSL2

```bash
# 1. Clone / enter project
cd secureops-sentinel

# 2. Build and start all services
docker compose up --build -d

# 3. Verify all containers are running
docker compose ps
```

**Access the stack:**

| Service | URL | Credentials |
|---------|-----|-------------|
| FastAPI docs | http://localhost:8000/docs | — |
| Prometheus | http://localhost:9090 | — |
| Grafana | http://localhost:3000 | admin / sentinel123 |

**Grafana dashboard:**  
Go to `Dashboards → SecureOps → SecureOps Sentinel`

---

## Triggering alerts manually

Use the FastAPI Swagger UI at `http://localhost:8000/docs` or curl:

```bash
# Trigger a brute-force spike (50 attempts)
curl -X POST "http://localhost:8000/simulate/brute-force?count=50"

# Spike failed logins
curl -X POST "http://localhost:8000/simulate/login-spike?count=30"

# Rate limit burst on /api/admin
curl -X POST "http://localhost:8000/simulate/rate-limit?endpoint=/api/admin&count=20"
```

## Stopping

```bash
docker compose down          # stop containers
docker compose down -v       # stop + delete volumes (reset all data)
```

---

## Phase roadmap

- [x] Phase 1 — Core metrics, Prometheus, Grafana dashboard
- [ ] Phase 2 — AlertManager + Slack webhook alerts, Bash log parser
- [ ] Phase 3 — AWS Lambda → CloudWatch integration, unified dashboard
