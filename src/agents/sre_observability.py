import time
from typing import Dict, Any, Optional
import random
from src.agents.base import BaseAgent, Anomaly
from src.metrics import (
    ANOMALIES_DETECTED,
    SYSTEM_CPU_USAGE,
    SYSTEM_MEMORY_USAGE,
    SYSTEM_DISK_USAGE,
    SERVICE_REQS_TOTAL,
    SERVICE_ERRORS_TOTAL
)

class SREObservabilityAgent(BaseAgent):
    """
    SRE_Observability_Agent: Monitors metric streams, registers metrics,
    and flags anomalies when a threshold is breached.
    """
    def __init__(self, name: str = "SRE_Observability_Agent"):
        super().__init__(name)
        # Configure thresholds
        self.thresholds = {
            "cpu_usage": 0.90,       # 90% CPU
            "memory_usage": 0.85,    # 85% Memory
            "disk_usage": 0.80,      # 80% Disk
            "database_error_rate": 5 # More than 5 errors in an interval
        }
        
    async def process(self, metrics: Dict[str, Any]) -> Optional[Anomaly]:
        """
        Process incoming metrics. If an anomaly is found, return an Anomaly object.
        """
        self.logger.info(
            f"Analyzing metrics: CPU={metrics.get('cpu_usage'):.2f}, "
            f"Memory={metrics.get('memory_usage'):.2f}, "
            f"Disk={metrics.get('disk_usage'):.2f}, "
            f"DB Errors={metrics.get('db_errors')}",
            extra={"agent_name": self.name}
        )

        # Update Prometheus metrics
        SYSTEM_CPU_USAGE.set(metrics.get("cpu_usage", 0.0))
        SYSTEM_MEMORY_USAGE.set(metrics.get("memory_usage", 0.0))
        SYSTEM_DISK_USAGE.set(metrics.get("disk_usage", 0.0))
        
        # Track simulated requests/errors
        SERVICE_REQS_TOTAL.labels(service_name="payment-gateway").inc(random.randint(10, 50))
        db_errors = metrics.get("db_errors", 0)
        if db_errors > 0:
            SERVICE_ERRORS_TOTAL.labels(service_name="payment-gateway", error_type="db_timeout").inc(db_errors)

        anomaly = None

        # Check CPU
        cpu = metrics.get("cpu_usage", 0.0)
        if cpu >= self.thresholds["cpu_usage"]:
            anomaly = Anomaly(
                metric_name="cpu_usage",
                current_value=cpu,
                threshold=self.thresholds["cpu_usage"],
                severity="CRITICAL" if cpu > 0.95 else "WARNING",
                description=f"CPU utilization is critical at {cpu*100:.1f}%",
                detected_at=time.time()
            )

        # Check Memory (only if CPU anomaly not already prioritized, or we can check all. For simplicity, check sequentially)
        elif metrics.get("memory_usage", 0.0) >= self.thresholds["memory_usage"]:
            mem = metrics["memory_usage"]
            anomaly = Anomaly(
                metric_name="memory_usage",
                current_value=mem,
                threshold=self.thresholds["memory_usage"],
                severity="CRITICAL" if mem > 0.92 else "WARNING",
                description=f"Memory utilization is high at {mem*100:.1f}% (Potential Memory Leak)",
                detected_at=time.time()
            )

        # Check Disk
        elif metrics.get("disk_usage", 0.0) >= self.thresholds["disk_usage"]:
            disk = metrics["disk_usage"]
            anomaly = Anomaly(
                metric_name="disk_usage",
                current_value=disk,
                threshold=self.thresholds["disk_usage"],
                severity="CRITICAL" if disk > 0.90 else "WARNING",
                description=f"Disk usage exceeded limit at {disk*100:.1f}%. Cache directory partition is filling up.",
                detected_at=time.time()
            )

        # Check DB Errors
        elif metrics.get("db_errors", 0) >= self.thresholds["database_error_rate"]:
            errors = metrics["db_errors"]
            anomaly = Anomaly(
                metric_name="database_error_rate",
                current_value=float(errors),
                threshold=float(self.thresholds["database_error_rate"]),
                severity="CRITICAL",
                description=f"Database errors are spiking. Encountered {errors} connection timeouts in the last polling interval.",
                detected_at=time.time()
            )

        if anomaly:
            self.logger.warning(
                f"Anomaly DETECTED: {anomaly.description}",
                extra={
                    "agent_name": self.name,
                    "anomaly_type": anomaly.metric_name,
                    "severity": anomaly.severity,
                    "anomaly_value": anomaly.current_value
                }
            )
            # Increment Prometheus counter
            ANOMALIES_DETECTED.labels(anomaly_type=anomaly.metric_name, severity=anomaly.severity).inc()

        return anomaly
