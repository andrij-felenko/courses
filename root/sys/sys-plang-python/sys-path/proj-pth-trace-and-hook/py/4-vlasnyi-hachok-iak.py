"""Стартовий гачок: вмикається на кожен запуск інтерпретатора. Має бути дешевий і німий."""

import os
import sys


def _configure() -> None:
    if os.environ.get("ZZ_BOOTSTRAP_OFF"):      # аварійний вимикач
        return
    # Нічого важкого тут не імпортуємо: цей код платить своєю ціною
    # за КОЖЕН запуск python у системі, включно з pip і мовним сервером IDE.
    sys.stdout.reconfigure(errors="backslashreplace")


try:
    _configure()
except Exception:                                # гачок не має права зривати старт
    import traceback
    traceback.print_exc()
