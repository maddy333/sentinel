import asyncio
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import uuid
from pydantic import BaseModel, Field

from src.logger import setup_logger

logger = setup_logger("agent-base")

class Anomaly(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    metric_name: str
    current_value: float
    threshold: float
    severity: str  # WARNING, CRITICAL
    description: str
    detected_at: float

class RemediationPlan(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    anomaly_id: str
    action: str  # e.g., restart_service, clear_disk, scale_deployment
    script: str  # The bash script to run
    risk_level: str  # LOW, MEDIUM, HIGH
    target_resource: str

class RemediationResult(BaseModel):
    plan_id: str
    success: bool
    output: str
    exit_code: int
    executed_at: float

class WorkflowContext(BaseModel):
    workflow_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    anomaly: Anomaly
    plan: Optional[RemediationPlan] = None
    result: Optional[RemediationResult] = None
    status: str = "DETECTED"  # DETECTED, PLAN_FORMULATED, EXECUTING, SUCCESS, FAILED
    created_at: float = Field(default_factory=lambda: asyncio.get_event_loop().time() if asyncio.get_event_loop().is_running() else 0.0)
    updated_at: float = Field(default_factory=lambda: asyncio.get_event_loop().time() if asyncio.get_event_loop().is_running() else 0.0)

    def update_status(self, new_status: str) -> None:
        self.status = new_status
        self.updated_at = asyncio.get_event_loop().time()

class BaseAgent(ABC):
    """
    Abstract Base Class for Async Agents.
    Provides basic logger, lifecycle management, and queue configuration.
    """
    def __init__(self, name: str):
        self.name = name
        self.logger = setup_logger(self.name)
        self._running = False

    async def start(self) -> None:
        self.logger.info(f"Starting agent {self.name}...", extra={"agent_name": self.name})
        self._running = True

    async def stop(self) -> None:
        self.logger.info(f"Stopping agent {self.name}...", extra={"agent_name": self.name})
        self._running = False

    @abstractmethod
    async def process(self, *args: Any, **kwargs: Any) -> Any:
        """
        Core logic of the agent. Must be implemented by subclasses.
        """
        pass
