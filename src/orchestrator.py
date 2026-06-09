import asyncio
import time
import random
from typing import Dict, List, Any, Optional
from src.logger import setup_logger
from src.agents.base import WorkflowContext
from src.agents.sre_observability import SREObservabilityAgent
from src.agents.devops_remediation import DevOpsRemediationAgent
from src.metrics import ACTIVE_WORKFLOWS, REMEDIATION_DURATION

class SentinelOrchestrator:
    """
    SentinelOrchestrator: Orchestrates SRE Observability and DevOps Remediation workflows.
    Runs a loop to monitor system health and resolve anomalies dynamically.
    """
    def __init__(self):
        self.logger = setup_logger("sentinel-orchestrator")
        self.sre_agent = SREObservabilityAgent()
        self.devops_agent = DevOpsRemediationAgent()
        
        # State management for API visibility
        self.workflows: Dict[str, WorkflowContext] = {}
        self._running = False
        self._task: Optional[asyncio.Task] = None
        
        # Anomaly Injection Queue
        self._anomaly_override: Optional[str] = None
        
        # Keep track of simulated metric baselines
        self.metric_baselines = {
            "cpu_usage": 0.35,
            "memory_usage": 0.55,
            "disk_usage": 0.65,
            "db_errors": 0
        }

    async def start(self) -> None:
        """
        Start agents and orchestration loop.
        """
        self._running = True
        await self.sre_agent.start()
        await self.devops_agent.start()
        self._task = asyncio.create_task(self._orchestration_loop())
        self.logger.info("Sentinel Orchestrator started successfully.")

    async def stop(self) -> None:
        """
        Stop agents and cancel background task.
        """
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        await self.sre_agent.stop()
        await self.devops_agent.stop()
        self.logger.info("Sentinel Orchestrator stopped.")

    def inject_anomaly(self, anomaly_type: str) -> bool:
        """
        Force injects an anomaly in the next cycle for simulation.
        Supported: cpu, memory, disk, db_errors
        """
        valid_types = ["cpu", "memory", "disk", "db_errors"]
        if anomaly_type in valid_types:
            self._anomaly_override = anomaly_type
            self.logger.info(f"Anomaly injection requested: {anomaly_type}")
            return True
        return False

    def get_system_metrics(self) -> Dict[str, Any]:
        """
        Simulate real-time system metrics with random drift.
        If an anomaly override is set, force it to cross threshold.
        """
        metrics = {}
        
        # Base drift
        cpu_drift = random.uniform(-0.05, 0.05)
        mem_drift = random.uniform(-0.02, 0.02)
        disk_drift = random.uniform(0.001, 0.005) # slowly growing
        
        # Update baseline
        self.metric_baselines["cpu_usage"] = max(0.1, min(0.89, self.metric_baselines["cpu_usage"] + cpu_drift))
        self.metric_baselines["memory_usage"] = max(0.2, min(0.84, self.metric_baselines["memory_usage"] + mem_drift))
        self.metric_baselines["disk_usage"] = max(0.1, min(0.79, self.metric_baselines["disk_usage"] + disk_drift))
        self.metric_baselines["db_errors"] = random.choice([0, 0, 0, 0, 0, 1, 0, 0, 0, 0]) # 10% chance of a single warning error
        
        # Copy values
        metrics["cpu_usage"] = self.metric_baselines["cpu_usage"]
        metrics["memory_usage"] = self.metric_baselines["memory_usage"]
        metrics["disk_usage"] = self.metric_baselines["disk_usage"]
        metrics["db_errors"] = self.metric_baselines["db_errors"]

        # Apply override if injected
        if self._anomaly_override:
            if self._anomaly_override == "cpu":
                metrics["cpu_usage"] = random.uniform(0.92, 0.98)
            elif self._anomaly_override == "memory":
                metrics["memory_usage"] = random.uniform(0.88, 0.96)
            elif self._anomaly_override == "disk":
                metrics["disk_usage"] = random.uniform(0.85, 0.95)
                # Ensure the baseline stays elevated so user can see remediation
                self.metric_baselines["disk_usage"] = metrics["disk_usage"]
            elif self._anomaly_override == "db_errors":
                metrics["db_errors"] = random.randint(8, 15)
            
            # Reset override
            self._anomaly_override = None

        return metrics

    async def _orchestration_loop(self) -> None:
        """
        Main simulation loop. Polls metrics every 5 seconds.
        """
        while self._running:
            try:
                metrics = self.get_system_metrics()
                # Run SRE agent monitoring
                anomaly = await self.sre_agent.process(metrics)
                
                if anomaly:
                    # Self-healing workflow triggered!
                    ACTIVE_WORKFLOWS.inc()
                    
                    context = WorkflowContext(anomaly=anomaly)
                    self.workflows[context.workflow_id] = context
                    self.logger.info(
                        f"Initialized self-healing Workflow {context.workflow_id}",
                        extra={"workflow_id": context.workflow_id, "anomaly_id": anomaly.id}
                    )
                    
                    # Spawn healing task concurrently so we don't block monitoring loop
                    asyncio.create_task(self._heal_anomaly(context))
                    
            except Exception as e:
                self.logger.error(f"Error in orchestrator loop: {e}", exc_info=True)
            
            await asyncio.sleep(5)

    async def _heal_anomaly(self, context: WorkflowContext) -> None:
        """
        Coordinates the self-healing workflow with the DevOps Agent.
        """
        start_time = time.time()
        workflow_id = context.workflow_id
        anomaly_type = context.anomaly.metric_name
        
        try:
            # Step 1: Formulate Plan
            context.update_status("PLAN_FORMULATED")
            plan = await self.devops_agent.process(context.anomaly)
            context.plan = plan
            self.workflows[workflow_id] = context
            
            # Step 2: Execute Plan
            context.update_status("EXECUTING")
            self.workflows[workflow_id] = context
            
            # Add minor delay for realistic transitions
            await asyncio.sleep(1)
            
            result = await self.devops_agent.execute_plan(plan)
            context.result = result
            
            # Step 3: Analyze outcome and apply post-healing adjustments
            if result.success:
                context.update_status("SUCCESS")
                self.logger.info(
                    f"Workflow {workflow_id} completed successfully. Self-healing resolved the issue.",
                    extra={"workflow_id": workflow_id, "status": "SUCCESS"}
                )
                
                # Apply simulated post-healing reset of baselines to clear the anomaly
                if anomaly_type == "cpu_usage":
                    self.metric_baselines["cpu_usage"] = 0.25
                elif anomaly_type == "memory_usage":
                    self.metric_baselines["memory_usage"] = 0.40
                elif anomaly_type == "disk_usage":
                    # Restoring disk to normal state
                    self.metric_baselines["disk_usage"] = 0.15
                elif anomaly_type == "database_error_rate":
                    self.metric_baselines["db_errors"] = 0
            else:
                context.update_status("FAILED")
                self.logger.error(
                    f"Workflow {workflow_id} failed during execution. Sandbox returned error exit code.",
                    extra={"workflow_id": workflow_id, "status": "FAILED"}
                )
                
        except Exception as e:
            context.update_status("FAILED")
            self.logger.error(
                f"Exception in workflow {workflow_id}: {e}", 
                exc_info=True, 
                extra={"workflow_id": workflow_id, "status": "FAILED"}
            )
        finally:
            # Telemetry update
            ACTIVE_WORKFLOWS.dec()
            duration = time.time() - start_time
            REMEDIATION_DURATION.labels(anomaly_type=anomaly_type).observe(duration)
            self.workflows[workflow_id] = context

    def get_workflows_summary(self) -> List[Dict[str, Any]]:
        """
        Returns a sorted list of recent workflows.
        """
        # Convert contexts to dicts
        items = []
        for w in self.workflows.values():
            items.append(w.model_dump())
        # Sort by updated_at descending
        return sorted(items, key=lambda x: x["updated_at"], reverse=True)
