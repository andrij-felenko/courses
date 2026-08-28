"""
Blue-Green Deployment Controller
Керує життєвим циклом двох середовищ, взаємодіє з L7-проксі
та автоматично ухвалює рішення про просування або відкат.
"""

from __future__ import annotations
import asyncio
import dataclasses
import enum
import logging
import time
from typing import Dict, List, Optional, Tuple

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] (%(name)s) %(message)s"
)
logger = logging.getLogger("BlueGreenController")


class EnvironmentRole(str, enum.Enum):
    BLUE = "blue"
    GREEN = "green"


class DeploymentPhase(str, enum.Enum):
    IDLE = "IDLE"
    PROVISIONING = "PROVISIONING"
    WARMING_UP = "WARMING_UP"
    SMOKE_TESTING = "SMOKE_TESTING"
    CUTOVER = "CUTOVER"
    SOAK_MONITORING = "SOAK_MONITORING"
    PROMOTED = "PROMOTED"
    ROLLING_BACK = "ROLLING_BACK"
    FAILED = "FAILED"


@dataclasses.dataclass(frozen=True)
class Endpoint:
    host: str
    port: int
    version: str

    @property
    def address(self) -> str:
        return f"{self.host}:{self.port}"


@dataclasses.dataclass
class EnvironmentState:
    role: EnvironmentRole
    version: str
    endpoints: List[Endpoint]
    is_active: bool = False
    is_warm: bool = False
    error_rate_percent: float = 0.0
    p99_latency_ms: float = 0.0


@dataclasses.dataclass(frozen=True)
class DeploymentConfig:
    app_name: str
    target_version: str
    warmup_requests_count: int = 50
    smoke_test_concurrency: int = 5
    soak_duration_seconds: float = 10.0
    max_allowed_error_rate: float = 1.0       # Максимум 1% помилок 5xx
    max_allowed_p99_latency_ms: float = 120.0  # Максимум 120 мс
    drain_timeout_seconds: float = 5.0
