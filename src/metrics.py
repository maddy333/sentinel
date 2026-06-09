from prometheus_client import Counter, Gauge, Histogram, make_wsgi_app
from fastapi import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware

# Define Prometheus metrics
ANOMALIES_DETECTED = Counter(
    "sentinel_anomalies_detected_total",
    "Total number of anomalies detected by the SRE Observability Agent",
    ["anomaly_type", "severity"]
)

REMEDIATIONS_TRIGGERED = Counter(
    "sentinel_remediations_triggered_total",
    "Total number of remediation actions executed by the DevOps Remediation Agent",
    ["action", "status"]
)

REMEDIATION_DURATION = Histogram(
    "sentinel_remediation_duration_seconds",
    "Time taken to resolve an anomaly through self-healing",
    ["anomaly_type"]
)

ACTIVE_WORKFLOWS = Gauge(
    "sentinel_active_workflows",
    "Number of active self-healing workflows currently running"
)

# Simulated Infrastructure Metrics
SYSTEM_CPU_USAGE = Gauge(
    "sentinel_system_cpu_usage_ratio",
    "Simulated system CPU usage ratio (0.0 to 1.0)"
)

SYSTEM_MEMORY_USAGE = Gauge(
    "sentinel_system_memory_usage_ratio",
    "Simulated system memory usage ratio (0.0 to 1.0)"
)

SYSTEM_DISK_USAGE = Gauge(
    "sentinel_system_disk_usage_ratio",
    "Simulated system disk usage ratio (0.0 to 1.0)"
)

SERVICE_REQS_TOTAL = Counter(
    "sentinel_service_requests_total",
    "Simulated total service requests processed",
    ["service_name"]
)

SERVICE_ERRORS_TOTAL = Counter(
    "sentinel_service_errors_total",
    "Simulated total service error count",
    ["service_name", "error_type"]
)

def register_metrics_endpoint(app: FastAPI) -> None:
    """
    Mount the Prometheus WSGI app to FastAPI's /metrics path
    """
    # Create the Prometheus WSGI app
    metrics_app = make_wsgi_app()
    # Mount it as middleware under /metrics
    app.mount("/metrics", WSGIMiddleware(metrics_app))
