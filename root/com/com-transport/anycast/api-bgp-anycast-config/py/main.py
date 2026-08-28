#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Агент перевірки працездатності для Anycast VIP через ExaBGP.
Вимоги: Python 3.8+
"""
import sys
import time
import signal
import urllib.request

VIP_PREFIX = "198.51.100.1/32"
HEALTH_URL = "http://127.0.0.1:8080/healthz"
CHECK_INTERVAL_SEC = 1.0
TIMEOUT_SEC = 0.5
RISE_THRESHOLD = 3   # Кількість успіхів поспіль для переходу в UP
FALL_THRESHOLD = 2   # Кількість помилок поспіль для переходу в DOWN

class AnycastHealthchecker:
    def __init__(self):
        self.state = "INIT"
        self.consecutive_successes = 0
        self.consecutive_failures = 0
        self.running = True

        # Коректне завершення роботи при отриманні сигналів SIGTERM/SIGINT
        signal.signal(signal.SIGTERM, self._handle_shutdown)
        signal.signal(signal.SIGINT, self._handle_shutdown)

    def _handle_shutdown(self, signum, frame):
        self.running = False
        self._withdraw()
        sys.exit(0)

    def _announce(self):
        sys.stdout.write(f"announce route {VIP_PREFIX} next-hop self\n")
        sys.stdout.flush()

    def _withdraw(self):
        sys.stdout.write(f"withdraw route {VIP_PREFIX}\n")
        sys.stdout.flush()

    def _check_service(self) -> bool:
        try:
            req = urllib.request.Request(HEALTH_URL, headers={"User-Agent": "Anycast-Probe/1.0"})
            with urllib.request.urlopen(req, timeout=TIMEOUT_SEC) as resp:
                return resp.status == 200
        except Exception:
            return False

    def run(self):
        while self.running:
            is_healthy = self._check_service()

            if is_healthy:
                self.consecutive_failures = 0
                self.consecutive_successes += 1
                if self.consecutive_successes >= RISE_THRESHOLD and self.state != "UP":
                    self.state = "UP"
                    self._announce()
            else:
                self.consecutive_successes = 0
                self.consecutive_failures += 1
                if self.consecutive_failures >= FALL_THRESHOLD and self.state != "DOWN":
                    self.state = "DOWN"
                    self._withdraw()

            time.sleep(CHECK_INTERVAL_SEC)

if __name__ == "__main__":
    checker = AnycastHealthchecker()
    checker.run()
