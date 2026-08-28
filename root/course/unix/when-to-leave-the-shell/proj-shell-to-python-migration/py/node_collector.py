#!/usr/bin/env python3
"""node_collector.py — надійний сервіс збору метрик кластера на Python."""

from __future__ import annotations

import argparse
import json
import logging
import os
import signal
import sys
import tempfile
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class NodeMetric:
    """Типізована структура метрик одного вузла."""
    node: str
    cpu_usage: float
    memory_free_mb: float
    status: str
    error: Optional[str] = None


@dataclass
class ClusterReport:
    """Підсумковий звіт стану кластера."""
    timestamp: str
    nodes_polled: int
    nodes_successful: int
    average_cpu_usage: float
    total_memory_free_mb: float
    nodes: List[NodeMetric]


def fetch_node_metrics(node: str, timeout_sec: float = 2.0) -> NodeMetric:
    """Опитування одного вузла через нативний HTTP-клієнт без виклику зовнішніх процесів."""
    url = f"http://{node}:9100/metrics.json"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "ClusterCollector/2.0"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout_sec) as response:
            if response.status != 200:
                return NodeMetric(
                    node=node,
                    cpu_usage=0.0,
                    memory_free_mb=0.0,
                    status="ERROR",
                    error=f"HTTP {response.status}",
                )
            payload = json.loads(response.read().decode("utf-8"))
            return NodeMetric(
                node=node,
                cpu_usage=float(payload.get("cpu_usage", 0.0)),
                memory_free_mb=float(payload.get("memory_free_mb", 0.0)),
                status=str(payload.get("status", "UNKNOWN")),
            )
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, ValueError) as exc:
        return NodeMetric(
            node=node,
            cpu_usage=0.0,
            memory_free_mb=0.0,
            status="ERROR",
            error=str(exc),
        )


def read_nodes_config(config_path: Path) -> List[str]:
    """Безпечне читання конфігурації без ризику розбиття на слова."""
    if not config_path.is_file():
        raise FileNotFoundError(f"Конфігураційний файл не знайдено: {config_path}")

    nodes = []
    with config_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                parts = line.split()
                if parts:
                    nodes.append(parts[0])
    return nodes


def atomic_write_json(data: dict, target_path: Path) -> None:
    """Атомарний запис звіту через тимчасовий файл і системний виклик rename(2).
    
    Тимчасовий файл створюється в тому самому каталозі, що й цільовий,
    оскільки rename(2) гарантує атомарність лише в межах однієї файлової системи.
    """
    target_path.parent.mkdir(parents=True, exist_ok=True)
    temp_file = tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=target_path.parent,
        delete=False,
        suffix=".tmp",
    )
    try:
        json.dump(data, temp_file, indent=2, ensure_ascii=False)
        temp_file.flush()
        os.fsync(temp_file.fileno())
        temp_file.close()
        # Атомарна заміна файлу (renameat2 / rename)
        os.replace(temp_file.name, target_path)
    except Exception:
        if os.path.exists(temp_file.name):
            os.remove(temp_file.name)
        raise


def collect_cluster_metrics(nodes: List[str], max_workers: int = 32) -> ClusterReport:
    """Паралельний збір метрик із контрольованим пулом воркерів."""
    results: List[NodeMetric] = []
    total_cpu = 0.0
    total_mem = 0.0
    successful_count = 0

    logger.info("Початок збору метрик для %d вузлів (пул: %d потоків)...", len(nodes), max_workers)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_node = {executor.submit(fetch_node_metrics, node): node for node in nodes}
        for future in as_completed(future_to_node):
            metric = future.result()
            results.append(metric)
            if metric.status == "OK":
                total_cpu += metric.cpu_usage
                total_mem += metric.memory_free_mb
                successful_count += 1

    avg_cpu = (total_cpu / successful_count) if successful_count > 0 else 0.0

    return ClusterReport(
        timestamp=datetime.now(timezone.utc).isoformat(),
        nodes_polled=len(nodes),
        nodes_successful=successful_count,
        average_cpu_usage=round(avg_cpu, 2),
        total_memory_free_mb=round(total_mem, 2),
        nodes=results,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Збирач метрик кластера")
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("/etc/cluster/nodes.conf"),
        help="Шлях до конфігураційного файлу вузлів",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("/var/log/cluster_reports/report.json"),
        help="Шлях до результуючого JSON-звіту",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=32,
        help="Кількість паралельних потоків",
    )
    args = parser.parse_args()

    # Обробка сигналів коректного завершення
    def handle_signal(signum, frame):
        logger.warning("Отримано сигнал %d, аварійне припинення роботи...", signum)
        sys.exit(128 + signum)

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    try:
        nodes = read_nodes_config(args.config)
        report = collect_cluster_metrics(nodes, max_workers=args.workers)
        atomic_write_json(asdict(report), args.out)
        logger.info("Звіт успішно збережено в %s", args.out)
        return 0
    except Exception as exc:
        logger.error("Критичний збій виконання: %s", exc, exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
