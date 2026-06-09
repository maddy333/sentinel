import asyncio
import time
import re
from typing import Dict, List, Tuple
from src.agents.base import BaseAgent, Anomaly, RemediationPlan, RemediationResult
from src.metrics import REMEDIATIONS_TRIGGERED

class SecureSandbox:
    """
    Simulated secure sandbox for shell script execution.
    Features command parsing, safety checks, and whitelisting.
    """
    def __init__(self):
        # Whitelisted commands patterns (regex)
        self.whitelist_patterns = [
            r"^rm\s+-rf\s+/tmp/cache/[a-zA-Z0-9_\-\.\*]*$",
            r"^systemctl\s+restart\s+(nginx|redis|payment-gateway)$",
            r"^docker\s+restart\s+(payment-db|auth-service)$",
            r"^kill\s+-9\s+\d+$",
            r"^pkill\s+-f\s+(memory_leak_app|leak_process)$",
            r"^echo\s+['\"][a-zA-Z0-9_\s\-\.\!\?]*['\"]\s*>\s*/tmp/recovery_flag$"
        ]
        
        # Blacklisted command patterns
        self.blacklist_patterns = [
            r"curl", r"wget", r"sh\s+-c", r"sudo", r"/etc/passwd", 
            r"rm\s+-rf\s+/\s*$", r"rm\s+-rf\s+\*(?!\/)", r"\b&&\b", r"\|"
        ]

    def validate_command(self, cmd: str) -> Tuple[bool, str]:
        """
        Validate if a single command is safe and fits the whitelist.
        """
        cmd = cmd.strip()
        if not cmd or cmd.startswith("#"):
            return True, "Comment or empty line"

        # Check blacklist first
        for pattern in self.blacklist_patterns:
            if re.search(pattern, cmd):
                return False, f"Security Violation: Blocked keyword/pattern '{pattern}' detected in command."

        # Check whitelist
        matched = False
        for pattern in self.whitelist_patterns:
            if re.match(pattern, cmd):
                matched = True
                break

        if not matched:
            return False, f"Security Violation: Command '{cmd}' is not in the sandbox whitelist of allowed commands."

        return True, "Safe"

    async def execute_script(self, script: str) -> Tuple[int, str]:
        """
        Executes the script inside the simulated sandbox line by line.
        """
        lines = [line.strip() for line in script.split("\n") if line.strip()]
        output_logs = []
        
        # Check shell safeguard configurations
        has_safeguards = False
        for line in lines:
            if line.startswith("set -"):
                has_safeguards = True
                output_logs.append(f"[sandbox-init] Safeguards active: {line}")

        for line in lines:
            if line.startswith("#") or line.startswith("set -"):
                continue
                
            is_valid, reason = self.validate_command(line)
            if not is_valid:
                output_logs.append(f"[sandbox-err] Command rejected: {line}")
                output_logs.append(f"[sandbox-err] Reason: {reason}")
                return 126, "\n".join(output_logs) + "\nExecution blocked by Sandbox Security Policy."

            # Simulate command execution
            output_logs.append(f"$ {line}")
            await asyncio.sleep(0.5) # Simulate execution latency
            
            # Simulated stdout based on commands
            if "rm -rf" in line:
                output_logs.append("Successfully cleaned 1.2 GB of cached assets.")
            elif "systemctl restart" in line:
                service = line.split()[-1]
                output_logs.append(f"Stopping {service}... Done.")
                output_logs.append(f"Starting {service}... Active (running).")
            elif "docker restart" in line:
                container = line.split()[-1]
                output_logs.append(f"Container '{container}' restarted successfully (Exit Code 0).")
            elif "pkill" in line or "kill" in line:
                output_logs.append("Process terminated. Memory release confirmed: 450MB reclaimed.")
            elif "echo" in line:
                output_logs.append("Recovery state written to flag file.")

        output_logs.append("[sandbox-info] Execution completed successfully.")
        return 0, "\n".join(output_logs)


class DevOpsRemediationAgent(BaseAgent):
    """
    DevOps_Remediation_Agent: Receives anomalies, formulates shell scripts,
    validates and executes them in a secure sandbox.
    """
    def __init__(self, name: str = "DevOps_Remediation_Agent"):
        super().__init__(name)
        self.sandbox = SecureSandbox()

    async def process(self, anomaly: Anomaly) -> RemediationPlan:
        """
        Formulate a shell script to resolve the anomaly.
        """
        self.logger.info(
            f"Formulating remediation plan for anomaly: {anomaly.metric_name}",
            extra={"agent_name": self.name, "anomaly_id": anomaly.id}
        )

        action = "unknown_remediation"
        script = "#!/usr/bin/env bash\nset -euo pipefail\n"
        risk_level = "LOW"
        target_resource = "infrastructure"

        if anomaly.metric_name == "cpu_usage":
            action = "restart_service"
            target_resource = "payment-gateway"
            risk_level = "MEDIUM"
            script += (
                f"# Remediation for high CPU utilization on {target_resource}\n"
                f"systemctl restart payment-gateway\n"
            )
        elif anomaly.metric_name == "memory_usage":
            action = "reclaim_memory"
            target_resource = "memory_leak_app"
            risk_level = "HIGH"
            script += (
                f"# Remediation for high memory usage on {target_resource}\n"
                f"pkill -f memory_leak_app\n"
            )
        elif anomaly.metric_name == "disk_usage":
            action = "clear_cache"
            target_resource = "/tmp/cache"
            risk_level = "LOW"
            script += (
                f"# Remediation for disk full on {target_resource}\n"
                f"rm -rf /tmp/cache/*\n"
            )
        elif anomaly.metric_name == "database_error_rate":
            action = "restart_db_container"
            target_resource = "payment-db"
            risk_level = "HIGH"
            script += (
                f"# Remediation for DB connection timeouts. Restarting payment-db container.\n"
                f"docker restart payment-db\n"
            )
        else:
            # Safe default fallback
            script += "echo 'Default status check' > /tmp/recovery_flag\n"

        plan = RemediationPlan(
            anomaly_id=anomaly.id,
            action=action,
            script=script,
            risk_level=risk_level,
            target_resource=target_resource
        )
        
        self.logger.info(
            f"Remediation plan formulated: {action} (Risk: {risk_level})",
            extra={
                "agent_name": self.name,
                "action": action,
                "risk_level": risk_level,
                "target_resource": target_resource,
                "script": script
            }
        )
        return plan

    async def execute_plan(self, plan: RemediationPlan) -> RemediationResult:
        """
        Executes the formulated plan in the sandbox.
        """
        self.logger.info(
            f"Executing remediation script for plan: {plan.id} (Action: {plan.action}) in sandbox...",
            extra={"agent_name": self.name, "plan_id": plan.id}
        )

        start_time = time.time()
        exit_code, output = await self.sandbox.execute_script(plan.script)
        execution_time = time.time() - start_time

        success = (exit_code == 0)
        status = "SUCCESS" if success else "FAILED"

        self.logger.info(
            f"Remediation script execution finished with status {status}. Exit Code: {exit_code}",
            extra={
                "agent_name": self.name,
                "plan_id": plan.id,
                "exit_code": exit_code,
                "output": output,
                "success": success,
                "execution_duration_sec": execution_time
            }
        )

        # Update Prometheus metrics
        REMEDIATIONS_TRIGGERED.labels(action=plan.action, status=status).inc()

        return RemediationResult(
            plan_id=plan.id,
            success=success,
            output=output,
            exit_code=exit_code,
            executed_at=start_time
        )
