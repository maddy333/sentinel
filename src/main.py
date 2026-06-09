import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse

from src.logger import setup_logger
from src.metrics import register_metrics_endpoint
from src.orchestrator import SentinelOrchestrator
from src.dashboard import DASHBOARD_HTML

logger = setup_logger("sentinel-service")
orchestrator = SentinelOrchestrator()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize the orchestrator
    logger.info("Initializing Sentinel orchestrator context...", extra={"status": "starting"})
    await orchestrator.start()
    yield
    # Shutdown: Stop the orchestrator
    logger.info("Stopping Sentinel orchestrator context...", extra={"status": "stopping"})
    await orchestrator.stop()

app = FastAPI(
    title="SentinelAI - Self-Healing Autonomous Ops",
    description="Multi-agent platform for autonomous infrastructure monitoring & recovery",
    version="1.0.0",
    lifespan=lifespan
)

# Register Prometheus metrics endpoint under /metrics
register_metrics_endpoint(app)

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    """
    Serves the beautiful dark-themed dashboard.
    """
    return DASHBOARD_HTML

@app.get("/healthz")
async def healthz():
    """
    Kubernetes liveness and readiness probe endpoint.
    Checks if the orchestrator and background task are operational.
    """
    if orchestrator._running and orchestrator._task and not orchestrator._task.done():
        return {"status": "healthy", "service": "sentinel-orchestrator"}
    
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Self-healing orchestration workflow loop is not running"
    )

@app.get("/workflows")
async def get_workflows():
    """
    Fetch the historical and active healing workflows.
    """
    return JSONResponse(content=orchestrator.get_workflows_summary())

@app.get("/stats")
async def get_stats():
    """
    Fetch the current active raw metrics for the dashboard's charts.
    """
    return JSONResponse(content={
        "cpu_usage": orchestrator.metric_baselines["cpu_usage"],
        "memory_usage": orchestrator.metric_baselines["memory_usage"],
        "disk_usage": orchestrator.metric_baselines["disk_usage"],
        "db_errors": orchestrator.metric_baselines["db_errors"]
    })

@app.post("/inject")
async def inject_anomaly(anomaly_type: str):
    """
    Injects an anomaly into the system.
    Supported: cpu, memory, disk, db_errors
    """
    success = orchestrator.inject_anomaly(anomaly_type)
    if success:
        return {"status": "ok", "message": f"Successfully injected {anomaly_type} anomaly"}
    
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Invalid anomaly type. Choose from: cpu, memory, disk, db_errors"
    )

if __name__ == "__main__":
    import uvicorn
    # In production/deployment, this is executed via uvicorn in Docker
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
