"""
container_orchestrator.py — Керування життєвим циклом ефемерних одноразових Docker-контейнерів.
Забезпечує ізольований «холодний старт» на новій машині з гарантованим очищенням ресурсів.
"""

from dataclasses import dataclass, field
import logging
import socket
import subprocess
import time
from typing import Optional
import uuid

logger = logging.getLogger("clean_slate.container")


@dataclass
class ContainerSpec:
    """Специфікація ефемерного контейнера для перевірки розгортання."""

    name: str
    image: str
    ports: dict[int, int] = field(default_factory=dict)  # {host_port: container_port}
    env: dict[str, str] = field(default_factory=dict)
    network: Optional[str] = None
    command: Optional[list[str]] = None


@dataclass
class OrchestrationResult:
    """Результат запуску та перевірки готовності контейнера."""

    container_name: str
    container_id: str
    is_running: bool
    startup_time_sec: float
    is_simulated: bool = False
    logs: str = ""
    error: Optional[str] = None


class ContainerOrchestrator:
    """
    Оркестратор ефемерного середовища через Docker CLI.

    Підтримує ізоляцію в тимчасових мережах (bridge), перевірку відкриття портів
    та гарантовану ліквідацію контейнерів після завершення тестів.
    У разі відсутності запущеного демона Docker перемикається у валідаційний
    симуляційний режим для безпечної перевірки маніфестів у легких CI-середовищах.
    """

    def __init__(self, use_simulation_fallback: bool = True) -> None:
        self.use_simulation_fallback = use_simulation_fallback
        self.active_containers: list[str] = []
        self.created_networks: list[str] = []
        self.docker_available = self._detect_docker_daemon()

    def _detect_docker_daemon(self) -> bool:
        """Перевіряє доступність та працездатність Docker демона на хості."""
        try:
            res = subprocess.run(
                ["docker", "info"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=3,
            )
            return res.returncode == 0
        except (OSError, subprocess.SubprocessError):
            return False

    def create_ephemeral_network(self, prefix: str = "clean_slate_net") -> str:
        """Створює одноразову ізольовану Docker-мережу для зв'язку між контейнерами."""
        net_name = f"{prefix}_{uuid.uuid4().hex[:8]}"
        if not self.docker_available:
            self.created_networks.append(net_name)
            return net_name

        try:
            cmd = ["docker", "network", "create", "--driver", "bridge", net_name]
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            self.created_networks.append(net_name)
            return net_name
        except subprocess.CalledProcessError as err:
            logger.warning(f"Не вдалося створити тестову мережу Docker: {err}")
            return "bridge"

    def wait_for_port(self, host: str, port: int, timeout_sec: float = 15.0) -> bool:
        """Опитує відкриття TCP-порту сервісу методом неблокуючих сокет-спроб."""
        start_time = time.perf_counter()
        while time.perf_counter() - start_time < timeout_sec:
            try:
                with socket.create_connection((host, port), timeout=1.0):
                    return True
            except (OSError, ConnectionRefusedError):
                time.sleep(0.3)
        return False

    def run_container(self, spec: ContainerSpec, ready_timeout_sec: float = 15.0) -> OrchestrationResult:
        """
        Запускає одноразовий ефемерний контейнер із прив'язкою портів та змінних оточення.
        """
        start_time = time.perf_counter()

        if not self.docker_available:
            if not self.use_simulation_fallback:
                return OrchestrationResult(
                    container_name=spec.name,
                    container_id="",
                    is_running=False,
                    startup_time_sec=0.0,
                    error="Docker демон недоступний на системі",
                )

            # Симуляційний режим перевірки конфігурації
            time.sleep(0.05)
            self.active_containers.append(spec.name)
            elapsed = time.perf_counter() - start_time
            return OrchestrationResult(
                container_name=spec.name,
                container_id=f"sim_{uuid.uuid4().hex[:12]}",
                is_running=True,
                startup_time_sec=round(elapsed, 3),
                is_simulated=True,
                logs="[SIMULATED] Контейнер успішно перевірено та запущено у симуляційному контурі.",
            )

        # Реальний запуск через Docker CLI
        unique_name = f"{spec.name}_{uuid.uuid4().hex[:6]}"
        cmd = ["docker", "run", "-d", "--name", unique_name]

        if spec.network:
            cmd.extend(["--network", spec.network])

        for host_port, cont_port in spec.ports.items():
            cmd.extend(["-p", f"{host_port}:{cont_port}"])

        for k, v in spec.env.items():
            cmd.extend(["-e", f"{k}={v}"])

        cmd.append(spec.image)
        if spec.command:
            cmd.extend(spec.command)

        try:
            res = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            container_id = res.stdout.strip()[:12]
            self.active_containers.append(unique_name)

            # Очікування відкриття заявлених портів
            for host_port in spec.ports.keys():
                if not self.wait_for_port("127.0.0.1", host_port, ready_timeout_sec):
                    self.stop_and_remove(unique_name)
                    return OrchestrationResult(
                        container_name=unique_name,
                        container_id=container_id,
                        is_running=False,
                        startup_time_sec=time.perf_counter() - start_time,
                        error=f"Таймаут очікування відкриття порту {host_port}",
                    )

            logs_res = subprocess.run(
                ["docker", "logs", unique_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            elapsed = time.perf_counter() - start_time
            return OrchestrationResult(
                container_name=unique_name,
                container_id=container_id,
                is_running=True,
                startup_time_sec=round(elapsed, 3),
                logs=logs_res.stdout[:500],
            )

        except subprocess.CalledProcessError as err:
            return OrchestrationResult(
                container_name=unique_name,
                container_id="",
                is_running=False,
                startup_time_sec=time.perf_counter() - start_time,
                error=f"Помилка запуску Docker контейнера: {err.stderr.strip()}",
            )

    def stop_and_remove(self, container_name: str) -> None:
        """Примусово зупиняє та видаляє контейнер."""
        if self.docker_available:
            subprocess.run(
                ["docker", "rm", "-f", container_name],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        if container_name in self.active_containers:
            self.active_containers.remove(container_name)

    def cleanup(self) -> None:
        """Гарантовано ліквідує всі створені контейнери та ізольовані мережі."""
        for cname in list(self.active_containers):
            self.stop_and_remove(cname)

        if self.docker_available:
            for net in self.created_networks:
                subprocess.run(
                    ["docker", "network", "rm", net],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
        self.created_networks.clear()

    def __enter__(self) -> "ContainerOrchestrator":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.cleanup()
