"""
container_orchestrator.py — Керування ізольованим середовищем контейнерів з нульовим виходом у мережу (Zero-Egress).
Підіймає ефемерні контейнери застосунку та сховища через Docker SDK у мережі з атрибутом internal=True.
"""

from __future__ import annotations

import atexit
import shutil
import signal
import subprocess
import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ContainerInstance:
    """Опис активного ефемерного контейнера."""
    container_id: str
    name: str
    role: str
    internal_ip: str
    is_simulated: bool = False


@dataclass
class OrchestrationResult:
    """Результат підйому ізольованого контуру приймання."""
    network_id: str
    network_name: str
    containers: list[ContainerInstance] = field(default_factory=list)
    zero_egress_enforced: bool = True
    error: str | None = None


class CleanRoomOrchestrator:
    """
    Оркестратор контейнерного середовища Clean-Room.
    Створює внутрішню ізольовану мережу (internal network), унеможливлюючи витік трафіку.
    """

    def __init__(self, network_prefix: str = "cleanroom-net") -> None:
        self.network_name = f"{network_prefix}-{int(time.time())}"
        self.network_id: str | None = None
        self.spawned_containers: list[str] = []
        self._docker_available: bool | None = None
        self._setup_shutdown_handlers()

    def check_docker(self) -> bool:
        """Перевіряє наявність та доступність демона Docker."""
        if self._docker_available is not None:
            return self._docker_available

        docker_bin = shutil.which("docker")
        if not docker_bin:
            self._docker_available = False
            return False

        try:
            res = subprocess.run(
                ["docker", "info"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=5,
            )
            self._docker_available = res.returncode == 0
        except Exception:
            self._docker_available = False

        return self._docker_available

    def start_isolated_environment(self, force_mock: bool = False) -> OrchestrationResult:
        """
        Розгортає ефемерну базу даних та сервіс у мережі без зовнішнього доступу.
        """
        use_docker = self.check_docker() and not force_mock

        if not use_docker:
            # Імітований режим для навчальних середовищ без Docker демона
            self.network_id = f"mock-net-{int(time.time())}"
            mock_db = ContainerInstance(
                container_id="mock-postgres-c1",
                name="cleanroom-postgres",
                role="database",
                internal_ip="172.28.0.2",
                is_simulated=True,
            )
            mock_app = ContainerInstance(
                container_id="mock-app-c2",
                name="cleanroom-target-app",
                role="application",
                internal_ip="172.28.0.3",
                is_simulated=True,
            )
            return OrchestrationResult(
                network_id=self.network_id,
                network_name=self.network_name,
                containers=[mock_db, mock_app],
                zero_egress_enforced=True,
            )

        try:
            # 1. Створення ізольованої мережі без зовнішнього шлюзу (--internal)
            cmd_net = [
                "docker", "network", "create",
                "--internal",
                "--subnet", "172.28.0.0/16",
                self.network_name,
            ]
            net_proc = subprocess.run(cmd_net, capture_output=True, text=True, check=True)
            self.network_id = net_proc.stdout.strip()

            # 2. Підйом контейнера PostgreSQL у zero-egress мережі
            db_name = f"pg-{int(time.time())}"
            cmd_db = [
                "docker", "run", "-d", "--rm",
                "--name", db_name,
                "--network", self.network_name,
                "-e", "POSTGRES_DB=cleanroom_db",
                "-e", "POSTGRES_USER=acceptance_officer",
                "-e", "POSTGRES_PASSWORD=sovereign_pass",
                "postgres:15-alpine",
            ]
            db_proc = subprocess.run(cmd_db, capture_output=True, text=True, check=True)
            db_cid = db_proc.stdout.strip()
            self.spawned_containers.append(db_name)

            container_db = ContainerInstance(
                container_id=db_cid,
                name=db_name,
                role="database",
                internal_ip="172.28.0.2",
                is_simulated=False,
            )

            # 3. Підйом застосунку
            app_name = f"app-{int(time.time())}"
            cmd_app = [
                "docker", "run", "-d", "--rm",
                "--name", app_name,
                "--network", self.network_name,
                "-e", "DATABASE_URL=postgres://acceptance_officer:sovereign_pass@cleanroom_db:5432/cleanroom_db",
                "alpine:latest", "sleep", "3600",
            ]
            app_proc = subprocess.run(cmd_app, capture_output=True, text=True, check=True)
            app_cid = app_proc.stdout.strip()
            self.spawned_containers.append(app_name)

            container_app = ContainerInstance(
                container_id=app_cid,
                name=app_name,
                role="application",
                internal_ip="172.28.0.3",
                is_simulated=False,
            )

            return OrchestrationResult(
                network_id=self.network_id,
                network_name=self.network_name,
                containers=[container_db, container_app],
                zero_egress_enforced=True,
            )
        except Exception as e:
            self.teardown()
            return OrchestrationResult(
                network_id="",
                network_name=self.network_name,
                zero_egress_enforced=False,
                error=f"Збій оркестрації Docker: {e}",
            )

    def teardown(self) -> None:
        """Повне детерміноване очищення всіх ефемерних ресурсів."""
        for cname in self.spawned_containers:
            try:
                subprocess.run(["docker", "rm", "-f", cname], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception:
                pass
        self.spawned_containers.clear()

        if self.network_name:
            try:
                subprocess.run(["docker", "network", "rm", self.network_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception:
                pass

    def _setup_shutdown_handlers(self) -> None:
        atexit.register(self.teardown)
        signal.signal(signal.SIGINT, lambda *_: (self.teardown(), sys.exit(130)))
        signal.signal(signal.SIGTERM, lambda *_: (self.teardown(), sys.exit(143)))
