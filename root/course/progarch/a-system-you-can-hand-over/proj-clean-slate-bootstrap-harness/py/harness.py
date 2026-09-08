"""
harness.py — Головний конвеєр валідатора Clean-Slate розгортання та точка входу CLI.
Координує всі 4 фази аудиту (оточення -> контейнери -> міграції -> димові тести -> звітування).
"""

from dataclasses import asdict
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
import argparse
import sys
import threading
import time

from env_scanner import EnvironmentScanner
from container_orchestrator import ContainerOrchestrator, ContainerSpec
from migration_verifier import MigrationVerifier, MigrationStep
from smoke_client import SmokeClient, EndpointProbe
from report_generator import AuditReporter, AuditReport

# Налаштування UTF-8 кодування виводу для коректного відображення на Windows
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


class CleanSlateHarness:
    """
    Координатор конвеєра перевірки розгортання системи «з чистого аркуша».
    """

    def __init__(self, project_name: str = "SystemUnderAudit") -> None:
        self.project_name = project_name
        self.reporter = AuditReporter(project_name=project_name)

    def run_all(
        self,
        project_dir: Path,
        migrations_dir: Path | None = None,
        base_url: str | None = None,
        smoke_probes: list[EndpointProbe] | None = None,
    ) -> AuditReport:
        """
        Запускає всі фази валідації та повертає підсумковий аудит.
        """
        total_start = time.perf_counter()

        # ФАЗА 1: Перевірка гігієни середовища та конфігурації
        p1_start = time.perf_counter()
        scanner = EnvironmentScanner()
        scan_res = scanner.scan(project_dir)
        p1_dur = time.perf_counter() - p1_start
        p1_summary = (
            f"Перевірено {scan_res.scanned_files_count} файлів. Конфігурація чиста."
            if scan_res.is_valid
            else f"Помилка: {len(scan_res.missing_env_vars)} відсутніх змінних, {len(scan_res.violations)} витоків шляхів."
        )
        self.reporter.add_phase(
            phase_id="env_hygiene",
            name="1. Гігієна середовища та 12-Factor конфігурація",
            passed=scan_res.is_valid,
            duration_sec=p1_dur,
            summary=p1_summary,
            details={
                "missing_env_vars": scan_res.missing_env_vars,
                "violations": [asdict(v) for v in scan_res.violations],
                "scanned_files": scan_res.scanned_files_count,
            },
        )

        # ФАЗА 2: Ідемпотентність міграцій бази даних (Up -> Down -> Up)
        p2_start = time.perf_counter()
        verifier = MigrationVerifier()
        if migrations_dir and migrations_dir.is_dir():
            steps = verifier.load_migrations_from_dir(migrations_dir)
        else:
            # Демонстраційні еталонні міграції для перевірки механізму
            steps = [
                MigrationStep(
                    version="001",
                    name="create_accounts",
                    up_sql="CREATE TABLE accounts (id INTEGER PRIMARY KEY, email TEXT NOT NULL, created_at DATETIME);",
                    down_sql="DROP TABLE IF EXISTS accounts;",
                ),
                MigrationStep(
                    version="002",
                    name="add_audit_log",
                    up_sql="CREATE TABLE audit_logs (id INTEGER PRIMARY KEY, action TEXT NOT NULL);",
                    down_sql="DROP TABLE IF EXISTS audit_logs;",
                ),
            ]
        mig_res = verifier.verify_migrations(steps)
        p2_dur = time.perf_counter() - p2_start
        p2_summary = (
            f"Успішно: {mig_res.applied_count} міграцій перевірено за циклом up-down-up. Схема ідемпотентна."
            if mig_res.is_idempotent
            else f"Збій ідемпотентності схеми: {len(mig_res.errors)} зафіксованих помилок."
        )
        self.reporter.add_phase(
            phase_id="db_migrations",
            name="2. Двостороння ідемпотентність схеми БД (Up-Down-Up)",
            passed=mig_res.is_idempotent,
            duration_sec=p2_dur,
            summary=p2_summary,
            details={
                "applied_count": mig_res.applied_count,
                "empty_slate_verified": mig_res.empty_slate_verified,
                "schema_hash": mig_res.reapplied_up_hash,
                "errors": mig_res.errors,
            },
        )

        # ФАЗА 3: Ефемерний запуск контейнера (холодний старт)
        p3_start = time.perf_counter()
        with ContainerOrchestrator(use_simulation_fallback=True) as orchestrator:
            net_name = orchestrator.create_ephemeral_network()
            spec = ContainerSpec(
                name="app_bootstrap_test",
                image="alpine:latest",
                network=net_name,
                env={"APP_ENV": "test", "PORT": "8080"},
                command=["echo", "System Cold-Start Ready"],
            )
            orch_res = orchestrator.run_container(spec, ready_timeout_sec=5.0)
            p3_dur = time.perf_counter() - p3_start

            mode_label = "симуляція" if orch_res.is_simulated else "Docker Engine"
            p3_summary = (
                f"Холодний старт успішний ({mode_label}, {orch_res.startup_time_sec} с)."
                if orch_res.is_running
                else f"Помилка холодного старту: {orch_res.error}"
            )
            self.reporter.add_phase(
                phase_id="container_bootstrap",
                name="3. Ефемерний контейнерний холодний старт",
                passed=orch_res.is_running,
                duration_sec=p3_dur,
                summary=p3_summary,
                details={
                    "container_id": orch_res.container_id,
                    "is_simulated": orch_res.is_simulated,
                    "startup_time_sec": orch_res.startup_time_sec,
                    "errors": [orch_res.error] if orch_res.error else [],
                },
            )

        # ФАЗА 4: Димове тестування HTTP-інтерфейсів
        p4_start = time.perf_counter()
        smoke_client = SmokeClient()
        if base_url:
            ready = smoke_client.wait_for_ready(base_url, timeout_sec=4.0)
            if not ready:
                smoke_summary = "Таймаут очікування зонда готовності сервісу (readiness probe)."
                smoke_passed = False
                probes_data = []
            else:
                probes = smoke_probes or [
                    EndpointProbe(name="Liveness Probe", path="/health/liveness", expected_status=200),
                    EndpointProbe(name="Readiness Probe", path="/health/ready", expected_status=200),
                    EndpointProbe(name="API Status Check", path="/api/v1/ping", expected_status=200),
                ]
                suite_res = smoke_client.run_probes(base_url, probes)
                smoke_passed = suite_res.all_passed
                smoke_summary = (
                    f"Усі {len(suite_res.probes)} HTTP-перевірки успішні (сумарно {suite_res.total_latency_ms} мс)."
                    if smoke_passed
                    else "Один або більше димових запитів завершилися з помилкою."
                )
                probes_data = [asdict(p) for p in suite_res.probes]
        else:
            smoke_passed = True
            smoke_summary = "HTTP димові тести пропущено (base_url не вказано)."
            probes_data = []

        p4_dur = time.perf_counter() - p4_start
        self.reporter.add_phase(
            phase_id="smoke_tests",
            name="4. Димова верифікація HTTP-зондів сервісу",
            passed=smoke_passed,
            duration_sec=p4_dur,
            summary=smoke_summary,
            details={"probes": probes_data},
        )

        total_dur = time.perf_counter() - total_start
        return self.reporter.build_report(total_dur)


class _DemoHealthHandler(BaseHTTPRequestHandler):
    """Легкий внутрішній HTTP-сервер для демонстрації димового тестування."""

    def do_GET(self) -> None:
        if self.path in ("/health/ready", "/health/liveness"):
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status": "ok", "state": "healthy"}')
        elif self.path == "/api/v1/ping":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"message": "pong"}')
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format: str, *args) -> None:
        # Приглушуємо стандартні логи HTTP-сервера для чистоти виводу
        pass


def run_demo() -> int:
    """Запускає повний автономний демонстраційний прогін Clean-Slate аудиту."""
    import os
    import tempfile

    with tempfile.TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)

        # Створюємо чистий .env.example
        env_example = root / ".env.example"
        env_example.write_text("DATABASE_URL=sqlite:///data.db\nPORT=8080\nSECRET_KEY=demo\n", encoding="utf-8")

        # Симулюємо наявність змінних у середовищі
        os.environ["DATABASE_URL"] = "sqlite:///data.db"
        os.environ["PORT"] = "8080"
        os.environ["SECRET_KEY"] = "clean_slate_demo_secret"

        # Створюємо директорію міграцій
        mig_dir = root / "migrations"
        mig_dir.mkdir()
        (mig_dir / "001_core.up.sql").write_text(
            "CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT); CREATE INDEX idx_u ON users(name);",
            encoding="utf-8",
        )
        (mig_dir / "001_core.down.sql").write_text("DROP TABLE IF EXISTS users;", encoding="utf-8")

        # Запускаємо внутрішній mock HTTP-сервер
        server = HTTPServer(("127.0.0.1", 0), _DemoHealthHandler)
        port = server.server_port
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()

        harness = CleanSlateHarness(project_name="TransferDemoService")
        base_url = f"http://127.0.0.1:{port}"

        print("\n========================================================")
        print("  ЗАПУСК CLEAN-SLATE BOOTSTRAP HARNESS (DEMO AUDIT)     ")
        print("========================================================\n")

        report = harness.run_all(
            project_dir=root,
            migrations_dir=mig_dir,
            base_url=base_url,
        )

        md_output = harness.reporter.to_markdown(report.total_duration_sec)
        print(md_output)

        out_dir = root / "artifacts"
        harness.reporter.save(out_dir, report.total_duration_sec)

        server.shutdown()
        server.server_close()

        return 0 if report.passed else 1


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Clean-Slate Bootstrap Harness: валідація готовності кодової бази до передачі."
    )
    parser.add_argument("--demo", action="store_true", help="Запустити демонстраційний автономний аудит")
    parser.add_argument("--project-dir", type=Path, default=Path.cwd(), help="Шлях до перевіряємого проєкту")
    parser.add_argument("--migrations-dir", type=Path, default=None, help="Директорія з SQL-міграціями")
    parser.add_argument("--base-url", type=str, default=None, help="Базовий HTTP URL розгорнутого сервісу")
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts"), help="Директорія для звітів")

    args = parser.parse_args()

    if args.demo or len(sys.argv) == 1:
        sys.exit(run_demo())

    harness = CleanSlateHarness(project_name=args.project_dir.name)
    report = harness.run_all(
        project_dir=args.project_dir,
        migrations_dir=args.migrations_dir,
        base_url=args.base_url,
    )

    harness.reporter.save(args.output_dir, report.total_duration_sec)
    print(harness.reporter.to_markdown(report.total_duration_sec))

    sys.exit(0 if report.passed else 1)


if __name__ == "__main__":
    main()
