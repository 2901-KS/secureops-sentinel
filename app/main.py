"""
SecureOps Sentinel — Security Event Metrics API
Simulates a real security service exposing Prometheus metrics.
"""

import random
import time
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from prometheus_client import (
    Counter, Gauge, Histogram, generate_latest, CONTENT_TYPE_LATEST
)
from fastapi.responses import Response

# ─── METRICS DEFINITIONS ─────────────────────────────────────────────────────

failed_logins = Counter(
    "security_failed_login_total",
    "Total number of failed login attempts",
    ["source_ip", "username"]
)

brute_force_attempts = Counter(
    "security_brute_force_attempts_total",
    "Total brute-force login attempts detected"
)

suspicious_ips = Gauge(
    "security_suspicious_ip_count",
    "Number of IPs currently flagged as suspicious"
)

rate_limit_violations = Counter(
    "security_rate_limit_violations_total",
    "Total API rate limit violations",
    ["endpoint"]
)

active_sessions = Gauge(
    "security_active_sessions_total",
    "Number of currently active authenticated sessions"
)

auth_latency = Histogram(
    "security_auth_latency_seconds",
    "Authentication request latency in seconds",
    buckets=[0.05, 0.1, 0.25, 0.5, 1.0, 2.0]
)

blocked_requests = Counter(
    "security_blocked_requests_total",
    "Total requests blocked by security rules",
    ["reason"]
)

alert_events = Counter(
    "security_alert_events_total",
    "Total security alerts triggered",
    ["severity"]
)

# ─── BACKGROUND SIMULATION ───────────────────────────────────────────────────

SUSPICIOUS_IPS = [
    "192.168.1.{i}".format(i=i) for i in range(10, 30)
]
USERNAMES = ["admin", "root", "user", "kinjal", "test", "api_user"]
ENDPOINTS = ["/api/login", "/api/data", "/api/admin", "/api/reset"]


async def simulate_security_events():
    """
    Background task: continuously emit realistic security events.
    This mimics what a real auth/security service would generate.
    """
    while True:
        # Simulate failed logins (steady trickle, occasional spike)
        n_fails = random.choices([1, 2, 5, 10], weights=[60, 25, 10, 5])[0]
        for _ in range(n_fails):
            ip = random.choice(SUSPICIOUS_IPS)
            user = random.choice(USERNAMES)
            failed_logins.labels(source_ip=ip, username=user).inc()

        # Brute force bursts (rare)
        if random.random() < 0.08:
            burst = random.randint(15, 40)
            brute_force_attempts.inc(burst)
            alert_events.labels(severity="critical").inc()

        # Suspicious IP count fluctuates
        suspicious_ips.set(random.randint(3, 25))

        # Rate limit violations
        if random.random() < 0.3:
            ep = random.choice(ENDPOINTS)
            rate_limit_violations.labels(endpoint=ep).inc(random.randint(1, 5))

        # Active sessions drift
        active_sessions.set(random.randint(40, 200))

        # Auth latency observation
        for _ in range(random.randint(3, 10)):
            latency = random.lognormvariate(-2, 0.6)  # realistic skew
            auth_latency.observe(min(latency, 3.0))

        # Blocked requests
        if random.random() < 0.2:
            reason = random.choice(["ip_blacklist", "rate_limit", "bad_token", "geo_block"])
            blocked_requests.labels(reason=reason).inc(random.randint(1, 8))

        # Info-level alerts
        if random.random() < 0.15:
            alert_events.labels(severity="warning").inc()

        await asyncio.sleep(5)


# ─── APP LIFECYCLE ────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(simulate_security_events())
    yield
    task.cancel()


app = FastAPI(
    title="SecureOps Sentinel",
    description="Security infrastructure observability API",
    lifespan=lifespan
)


# ─── ROUTES ──────────────────────────────────────────────────────────────────

@app.get("/", tags=["Health"])
def root():
    return {
        "service": "SecureOps Sentinel",
        "status": "running",
        "metrics_endpoint": "/metrics"
    }


@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy"}


@app.get("/metrics", tags=["Observability"])
def metrics():
    """Prometheus scrape endpoint — exposes all security metrics."""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


# ─── MANUAL TRIGGER ENDPOINTS ─────────────────────────────────────────────────
# Lets you spike metrics manually to test alert thresholds in Grafana

@app.post("/simulate/brute-force", tags=["Simulation"])
def trigger_brute_force(count: int = 50):
    """Manually trigger a brute-force spike to test alerting."""
    brute_force_attempts.inc(count)
    alert_events.labels(severity="critical").inc()
    return {"triggered": "brute_force", "count": count}


@app.post("/simulate/login-spike", tags=["Simulation"])
def trigger_login_spike(count: int = 30):
    """Manually spike failed logins from a single IP."""
    ip = "10.0.0.99"
    for _ in range(count):
        failed_logins.labels(source_ip=ip, username="admin").inc()
    return {"triggered": "login_spike", "count": count}


@app.post("/simulate/rate-limit", tags=["Simulation"])
def trigger_rate_limit(endpoint: str = "/api/admin", count: int = 20):
    """Manually trigger rate limit violations on a given endpoint."""
    rate_limit_violations.labels(endpoint=endpoint).inc(count)
    return {"triggered": "rate_limit", "endpoint": endpoint, "count": count}
