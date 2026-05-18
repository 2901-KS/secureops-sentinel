# SecureOps Sentinel 
 
> **Security Infrastructure Observability Stack**
> Built to mirror real-world InfoSec SRE workflows — real-time threat detection, automated alerting, and multi-source metric ingestion using industry-standard tools.
 
---
 
## What is SecureOps Sentinel?
 
Most monitoring tools tell you something went wrong *after* it happened. **SecureOps Sentinel is built to catch it while it's happening.**
 
It simulates a production security service — generating realistic threat signals like brute-force bursts, suspicious IP clusters, and API rate violations — then runs them through a full observability pipeline: metrics scraped by Prometheus every 15 seconds, visualised across 8 live Grafana panels, and routed through AlertManager to fire Slack notifications the moment a threshold is breached.
 
What makes this different from a typical monitoring demo:
 
- **Security-first metrics** — not CPU or memory, but `failed_login_total`, `brute_force_attempts`, `suspicious_ip_count` — the signals a real InfoSec team tracks
- **Dual ingestion paths** — FastAPI exposes a `/metrics` endpoint for Prometheus pull; a Bash log parser pushes structured metrics to Pushgateway independently
- **Severity-aware alerting** — critical and warning alerts route to separate Slack receivers with different formatting and repeat intervals
- **Fully containerised** — one `docker compose up` brings up 5 services with zero manual configuration
- **Simulation endpoints** — `/simulate/brute-force`, `/simulate/login-spike`, `/simulate/rate-limit` let you fire real incidents on demand and watch the pipeline respond in real time

---

## Architecture

```
FastAPI /metrics  ──►  Prometheus (scrape every 15s)  ──►  Grafana dashboards
     │                        │                                    │
     │                  alert_rules.yml                     8 security panels
     │                        │                              alert rules
     ▼                        ▼                                    │
Simulation endpoints    AlertManager  ──────────────────►  Slack #new-channel 🚨
/simulate/brute-force        │
/simulate/login-spike        │
/simulate/rate-limit         ▼
                        Pushgateway  ◄──  log_parser.sh (Bash)
```

---

## Stack

| Component | Purpose |
|-----------|---------|
| FastAPI | Security event simulator + `/metrics` endpoint |
| Prometheus | Scrapes and stores time-series metrics (15s interval) |
| Grafana | Dashboards, visualisations, alert rules |
| AlertManager | Routes alerts to Slack based on severity |
| Pushgateway | Receives metrics pushed by Bash log parser |
| Docker Compose | Orchestrates the full 5-container stack |

---

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

## Screenshots

### Grafana Dashboard — Live Security Metrics

<img width="1845" height="786" alt="Screenshot 2026-05-18 143047" src="https://github.com/user-attachments/assets/b7130c38-a1fc-4c63-aa56-f2dc2db719df" />

<img width="1842" height="630" alt="image" src="https://github.com/user-attachments/assets/bd1be248-6af7-44fa-adb7-d2b0fb485b14" />

### Brute Force Spike — Real-time Detection
<img width="1861" height="908" alt="Screenshot 2026-05-18 115707" src="https://github.com/user-attachments/assets/fa04bc89-15a8-46ec-a1f0-6b4e99f285ac" />


### Prometheus Targets — All UP 
<img width="1855" height="917" alt="Screenshot 2026-05-18 143127" src="https://github.com/user-attachments/assets/58857b29-5956-40e7-ab81-52b2079cfa00" />


### FastAPI Docs — Simulation Endpoints
<img width="1827" height="891" alt="Screenshot 2026-05-18 143143" src="https://github.com/user-attachments/assets/4c5adf48-71cf-4afe-9f22-dc30501d9b32" />


### Slack Alert — CRITICAL BruteForceSpike
<img width="1866" height="848" alt="Screenshot 2026-05-18 143240" src="https://github.com/user-attachments/assets/c722e20d-14dc-4c00-a65f-23d343798b5f" />


---

## Quick start

**Prerequisites:** Docker Desktop running on WSL2

```bash
git clone https://github.com/2901-KS/secureops-sentinel.git
cd secureops-sentinel
docker compose up --build -d
docker compose ps
```

**Access the stack:**

| Service | URL | Credentials |
|---------|-----|-------------|
| FastAPI docs | http://localhost:8000/docs | — |
| Prometheus | http://localhost:9090 | — |
| Grafana | http://localhost:3000 | admin / sentinel123 |
| AlertManager | http://localhost:9093 | — |
| Pushgateway | http://localhost:9091 | — |

**Grafana dashboard:**
`Dashboards → SecureOps → SecureOps Sentinel`

---

## Triggering alerts manually

```bash
# Brute-force spike
curl -X POST "http://localhost:8000/simulate/brute-force?count=100"

# Failed login spike
curl -X POST "http://localhost:8000/simulate/login-spike?count=30"

# Rate limit burst
curl -X POST "http://localhost:8000/simulate/rate-limit?endpoint=/api/admin&count=20"
```

## Bash log parser (Pushgateway)

```bash
# Run in WSL
chmod +x log_parser.sh
./log_parser.sh
```

Parses `security.log` every 30s and pushes metrics to Pushgateway at `localhost:9091`.

## Secrets management

Slack webhook URL is stored in `alertmanager/alertmanager.yml` locally.
This file is in `.gitignore` — never committed to version control.
Use a `.env` file for all secrets in production.

---

## Stopping

```bash
docker compose down        # stop containers
docker compose down -v     # stop + delete volumes
```

---

## Phase roadmap

- [x] Phase 1 — Core metrics, Prometheus, Grafana dashboard (8 panels)
- [x] Phase 2 — AlertManager, Slack webhook alerts, Bash log parser, Pushgateway
- [ ] Phase 3 — AWS CloudWatch / GCP Cloud Operations integration (account setup pending )- working on it
