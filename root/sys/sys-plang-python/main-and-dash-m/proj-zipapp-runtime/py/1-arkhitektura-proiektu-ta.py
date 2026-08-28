import os
import platform
import sys


def collect_metrics() -> dict[str, str | int]:
    """Збирає базову інформацію про середовище виконання."""
    load_avg = os.getloadavg() if hasattr(os, "getloadavg") else (0.0, 0.0, 0.0)
    return {
        "platform": platform.platform(),
        "python_version": sys.version.split()[0],
        "pid": os.getpid(),
        "load_1m": load_avg[0],
        "load_5m": load_avg[1],
        "load_15m": load_avg[2],
    }
