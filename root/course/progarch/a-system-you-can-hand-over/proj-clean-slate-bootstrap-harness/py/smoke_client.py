"""
smoke_client.py — Димовий HTTP-клієнт для верифікації розгорнутого сервісу.
Перевіряє готовність (readiness/liveness) зондів та базові бізнес-ендпоінти.
"""

from dataclasses import dataclass, field
import json
import time
from typing import Optional
import urllib.error
import urllib.request


@dataclass
class EndpointProbe:
    """Опис контрольного HTTP-ендпоінта для перевірки здоров'я застосунку."""

    name: str
    path: str
    method: str = "GET"
    expected_status: int = 200
    payload: Optional[dict] = None
    headers: dict[str, str] = field(default_factory=dict)
    timeout_sec: float = 4.0


@dataclass
class ProbeResult:
    """Результат виконання окремого димового запиту."""

    name: str
    url: str
    passed: bool
    status_code: int
    latency_ms: float
    error_message: Optional[str] = None
    response_body_sample: str = ""


@dataclass
class SmokeSuiteResult:
    """Підсумок димового тестування сервісу."""

    all_passed: bool
    probes: list[ProbeResult]
    total_latency_ms: float


class SmokeClient:
    """
    Автономний HTTP-клієнт для перевірки працездатності розгорнутого сервісу.
    Використовує виключно стандартну бібліотеку Python без зовнішніх залежностей.
    """

    def wait_for_ready(
        self,
        base_url: str,
        ready_path: str = "/health/ready",
        timeout_sec: float = 12.0,
        poll_interval_sec: float = 0.5,
    ) -> bool:
        """
        Блокує виконання до тих пір, поки зонд готовності не поверне HTTP 200 або не вичерпається таймаут.
        """
        clean_base = base_url.rstrip("/")
        url = f"{clean_base}/{ready_path.lstrip('/')}"
        start_time = time.perf_counter()

        while time.perf_counter() - start_time < timeout_sec:
            try:
                req = urllib.request.Request(url, method="GET")
                with urllib.request.urlopen(req, timeout=1.5) as resp:
                    if resp.status == 200:
                        return True
            except (OSError, urllib.error.URLError):
                time.sleep(poll_interval_sec)

        return False

    def run_probes(
        self, base_url: str, probes: list[EndpointProbe]
    ) -> SmokeSuiteResult:
        """
        Виконує набір перевірочних запитів та збирає метрики латентності і кодів відповідей.
        """
        clean_base = base_url.rstrip("/")
        results: list[ProbeResult] = []
        total_latency = 0.0
        all_passed = True

        for probe in probes:
            url = f"{clean_base}/{probe.path.lstrip('/')}"
            data = None
            headers = dict(probe.headers)

            if probe.payload is not None:
                data = json.dumps(probe.payload).encode("utf-8")
                headers["Content-Type"] = "application/json"

            req = urllib.request.Request(url, data=data, headers=headers, method=probe.method)

            start = time.perf_counter()
            status_code = 0
            error_msg = None
            body_sample = ""
            passed = False

            try:
                with urllib.request.urlopen(req, timeout=probe.timeout_sec) as resp:
                    latency = (time.perf_counter() - start) * 1000.0
                    status_code = resp.status
                    raw_body = resp.read()
                    body_sample = raw_body.decode("utf-8", errors="ignore")[:100]
                    passed = (status_code == probe.expected_status)

            except urllib.error.HTTPError as ex:
                latency = (time.perf_counter() - start) * 1000.0
                status_code = ex.code
                error_msg = f"HTTP {ex.code}: {ex.reason}"
                passed = (status_code == probe.expected_status)

            except Exception as ex:
                latency = (time.perf_counter() - start) * 1000.0
                error_msg = f"Збій з'єднання: {str(ex)}"
                passed = False

            total_latency += latency
            if not passed:
                all_passed = False

            results.append(
                ProbeResult(
                    name=probe.name,
                    url=url,
                    passed=passed,
                    status_code=status_code,
                    latency_ms=round(latency, 2),
                    error_message=error_msg,
                    response_body_sample=body_sample.strip(),
                )
            )

        return SmokeSuiteResult(
            all_passed=all_passed,
            probes=results,
            total_latency_ms=round(total_latency, 2),
        )
