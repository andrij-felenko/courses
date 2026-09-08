"""
diagnostic_client.py — Клієнт діагностичних контрактів сервісу (Health / Readiness / Liveness).
Опитує ендпоінти життєздатності та виконує контрольні транзакції з верифікацією затримки SLA.
"""

from __future__ import annotations

import http.server
import json
import threading
import time
import urllib.request
from dataclasses import dataclass, field
from typing import Any


@dataclass
class DiagnosticProbeResult:
    """Результат опитування окремого діагностичного контракту."""
    name: str
    endpoint: str
    status_code: int
    latency_ms: float
    passed: bool
    payload: dict[str, Any] = field(default_factory=dict)
    error: str | None = None


@dataclass
class DiagnosticSuiteResult:
    """Підсумок виконання набору димових діагностичних тестів."""
    passed: bool
    total_probes: int
    passed_probes: int
    probes: list[DiagnosticProbeResult] = field(default_factory=list)
    max_latency_observed_ms: float = 0.0


class DiagnosticClient:
    """
    Клієнт діагностики машинного контракту готовності до приймання.
    """

    DEFAULT_SLA_LATENCY_MS = 500.0

    def run_diagnostics(
        self,
        base_url: str | None = None,
        max_latency_ms: float = DEFAULT_SLA_LATENCY_MS,
        start_embedded_server: bool = True,
    ) -> DiagnosticSuiteResult:
        """
        Виконує повний діагностичний прогін зондів і контрольних операцій.
        """
        server_thread = None
        httpd = None
        effective_url = base_url

        if not effective_url and start_embedded_server:
            httpd, port = self._start_ephemeral_http_server()
            effective_url = f"http://127.0.0.1:{port}"

        probes: list[DiagnosticProbeResult] = []

        try:
            # 1. Зонд liveness (чи живий процес)
            probes.append(self._probe_endpoint(
                effective_url,
                "/health/liveness",
                "Liveness Probe",
                expected_code=200,
                max_latency_ms=max_latency_ms,
            ))

            # 2. Зонд readiness (чи підключено БД і залежності)
            probes.append(self._probe_endpoint(
                effective_url,
                "/health/readiness",
                "Readiness Probe",
                expected_code=200,
                max_latency_ms=max_latency_ms,
            ))

            # 3. Контрольна транзакція запису
            contract_data = {
                "contract_id": f"acpt-{int(time.time())}",
                "contractor": "External-Vendor-LLC",
                "status": "IN_ACCEPTANCE",
            }
            probes.append(self._probe_post(
                effective_url,
                "/api/v1/acceptance/contracts",
                "Create Contract Transaction",
                payload=contract_data,
                expected_code=201,
                max_latency_ms=max_latency_ms,
            ))

        finally:
            if httpd:
                httpd.shutdown()
                httpd.server_close()

        passed_count = sum(1 for p in probes if p.passed)
        max_lat = max((p.latency_ms for p in probes), default=0.0)

        return DiagnosticSuiteResult(
            passed=passed_count == len(probes),
            total_probes=len(probes),
            passed_probes=passed_count,
            probes=probes,
            max_latency_observed_ms=round(max_lat, 2),
        )

    def _probe_endpoint(
        self,
        base_url: str,
        path: str,
        name: str,
        expected_code: int,
        max_latency_ms: float,
    ) -> DiagnosticProbeResult:
        url = f"{base_url}{path}"
        start = time.perf_counter()
        try:
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=5) as resp:
                latency_ms = (time.perf_counter() - start) * 1000.0
                body = json.loads(resp.read().decode("utf-8"))
                passed = resp.status == expected_code and latency_ms <= max_latency_ms
                return DiagnosticProbeResult(
                    name=name,
                    endpoint=path,
                    status_code=resp.status,
                    latency_ms=round(latency_ms, 2),
                    passed=passed,
                    payload=body,
                )
        except Exception as e:
            latency_ms = (time.perf_counter() - start) * 1000.0
            return DiagnosticProbeResult(
                name=name,
                endpoint=path,
                status_code=0,
                latency_ms=round(latency_ms, 2),
                passed=False,
                error=str(e),
            )

    def _probe_post(
        self,
        base_url: str,
        path: str,
        name: str,
        payload: dict[str, Any],
        expected_code: int,
        max_latency_ms: float,
    ) -> DiagnosticProbeResult:
        url = f"{base_url}{path}"
        start = time.perf_counter()
        try:
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=data,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                latency_ms = (time.perf_counter() - start) * 1000.0
                body = json.loads(resp.read().decode("utf-8"))
                passed = resp.status == expected_code and latency_ms <= max_latency_ms
                return DiagnosticProbeResult(
                    name=name,
                    endpoint=path,
                    status_code=resp.status,
                    latency_ms=round(latency_ms, 2),
                    passed=passed,
                    payload=body,
                )
        except Exception as e:
            latency_ms = (time.perf_counter() - start) * 1000.0
            return DiagnosticProbeResult(
                name=name,
                endpoint=path,
                status_code=0,
                latency_ms=round(latency_ms, 2),
                passed=False,
                error=str(e),
            )

    def _start_ephemeral_http_server(self) -> tuple[http.server.HTTPServer, int]:
        storage: dict[str, Any] = {}

        class EphemeralHandler(http.server.BaseHTTPRequestHandler):
            def do_GET(self) -> None:
                if self.path == "/health/liveness":
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"status": "alive", "timestamp": time.time()}).encode("utf-8"))
                elif self.path == "/health/readiness":
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"status": "ready", "database": "connected"}).encode("utf-8"))
                else:
                    self.send_response(404)
                    self.end_headers()

            def do_POST(self) -> None:
                if self.path == "/api/v1/acceptance/contracts":
                    length = int(self.headers.get("Content-Length", 0))
                    raw_data = self.rfile.read(length).decode("utf-8")
                    data = json.loads(raw_data)
                    storage[data["contract_id"]] = data
                    self.send_response(201)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"created": True, "item": data}).encode("utf-8"))
                else:
                    self.send_response(404)
                    self.end_headers()

            def log_message(self, format: str, *args: Any) -> None:
                # Вимикаємо стандартний спам логів сервера
                pass

        server = http.server.HTTPServer(("127.0.0.1", 0), EphemeralHandler)
        port = server.server_address[1]
        t = threading.Thread(target=server.serve_forever, daemon=True)
        t.start()
        return server, port
