import httpx
import pytest

BASE_URL = "http://localhost:8000"

@pytest.mark.asyncio
async def test_diagnostics_contract_compliance():
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        # 1. Перевірка відповіді ендпойнта liveness
        live_resp = await client.get("/healthz", timeout=1.5)
        assert live_resp.status_code == 200, "Liveness probe must return 200 OK"
        assert "application/health+json" in live_resp.headers.get("content-type", "")
        assert live_resp.headers.get("cache-control") == "no-cache, no-store, must-revalidate"

        # 2. Перевірка відповіді ендпойнта readiness
        ready_resp = await client.get("/ready", timeout=1.5)
        assert ready_resp.status_code == 200, "Readiness probe must return 200 OK"
        data = ready_resp.json()
        assert data.get("status") == "pass"

@pytest.mark.asyncio
async def test_probe_isolation_during_database_outage(mock_db_failure):
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        # Імітуємо падіння зовнішнього зв'язку з БД
        await mock_db_failure.trigger_disconnect()

        # Сервіс зобов'язаний вимкнути прийом трафіку
        ready_resp = await client.get("/ready", timeout=2.0)
        assert ready_resp.status_code == 503, (
            "Readiness must return 503 when downstream dependency fails"
        )
        data = ready_resp.json()
        assert data.get("status") == "fail"

        # Архітектурний інваріант: Liveness зобов'язаний залишатися 200 OK
        live_resp = await client.get("/healthz", timeout=1.0)
        assert live_resp.status_code == 200, (
            "FATAL: Liveness probe returned failure on downstream outage! "
            "This will cause a cascading restart storm."
        )

        # Перевірка на відсутність паролів і секретів у тілі діагностичного звіту
        raw_body = ready_resp.text
        forbidden_patterns = ["password", "secret", "bearer", "postgres://", "traceback"]
        for pattern in forbidden_patterns:
            assert pattern not in raw_body.lower(), (
                f"Security breach: Sensitive keyword '{pattern}' leaked in health report!"
            )
