"""
Тестовий емулятор стороннього API на aiohttp.web із перевіркою ідемпотентності та хаос-інжекцією.
"""

import asyncio
import random
from typing import Any, Optional

from aiohttp import web


class MockPartnerServer:
    """
    Легковагий тестовий сервер на aiohttp.web для перевірки надійності Outbox конвеєра.
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 0):
        self.host = host
        self.port = port
        self.app = web.Application()
        self.runner: Optional[web.AppRunner] = None
        self.site: Optional[web.TCPSite] = None
        self.actual_port: int = 0

        self.received_keys: dict[str, dict[str, Any]] = {}
        self.call_count: int = 0
        self.duplicate_count: int = 0

        self.chaos_fail_rate: float = 0.0
        self.chaos_latency_s: float = 0.0
        self.fatal_event_types: set[str] = set()
        self.drop_response_keys: set[str] = set()

        self._setup_routes()

    def _setup_routes(self) -> None:
        self.app.router.add_post("/api/v1/events", self._handle_event)
        self.app.router.add_get("/api/v1/stats", self._handle_stats)

    async def _handle_event(self, request: web.Request) -> web.Response:
        self.call_count += 1
        idem_key = request.headers.get("Idempotency-Key")

        if not idem_key:
            return web.json_response(
                {"error": "Missing required Idempotency-Key header"},
                status=400,
            )

        data = await request.json()
        event_type = data.get("event_type", "")

        if self.chaos_latency_s > 0:
            await asyncio.sleep(self.chaos_latency_s)

        # 1. Симуляція отруйного повідомлення (400 Bad Request — NonRetryable)
        if event_type in self.fatal_event_types:
            return web.json_response(
                {"error": "Invalid business payload format (Poison Pill)"},
                status=400,
            )

        # 2. Перевірка існуючого ключа ідемпотентності
        if idem_key in self.received_keys:
            self.duplicate_count += 1
            cached = self.received_keys[idem_key]
            return web.json_response(
                {
                    "status": "DEDUPLICATED",
                    "idempotency_key": idem_key,
                    "original_tx_id": cached["tx_id"],
                    "message": "Duplicate mutation suppressed by idempotency guard",
                },
                status=200,
            )

        # 3. Симуляція скидання зв'язку після успішної фіксації на сервері (Two Generals Problem)
        if idem_key in self.drop_response_keys:
            self.drop_response_keys.remove(idem_key)
            tx_id = f"tx-{len(self.received_keys) + 1:04d}"
            self.received_keys[idem_key] = {
                "tx_id": tx_id,
                "event_id": data.get("event_id"),
                "timestamp": asyncio.get_event_loop().time(),
            }
            raise web.HTTPServiceUnavailable(reason="Network connection dropped on response path")

        # 4. Хаос-інжекція транзитної 503 помилки
        if self.chaos_fail_rate > 0 and random.random() < self.chaos_fail_rate:
            return web.json_response(
                {"error": "Service Temporarily Unavailable (Flaky Gateway)"},
                status=503,
            )

        # 5. Штатна обробка
        tx_id = f"tx-{len(self.received_keys) + 1:04d}"
        response_record = {
            "tx_id": tx_id,
            "event_id": data.get("event_id"),
            "timestamp": asyncio.get_event_loop().time(),
        }
        self.received_keys[idem_key] = response_record

        return web.json_response(
            {
                "status": "ACCEPTED",
                "tx_id": tx_id,
                "idempotency_key": idem_key,
            },
            status=200,
        )

    async def _handle_stats(self, request: web.Request) -> web.Response:
        return web.json_response({
            "call_count": self.call_count,
            "duplicate_count": self.duplicate_count,
            "unique_keys": len(self.received_keys),
        })

    async def start(self) -> str:
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        self.site = web.TCPSite(self.runner, self.host, self.port)
        await self.site.start()

        for s in self.runner.sites:
            if isinstance(s, web.TCPSite):
                for sock in s._server.sockets:
                    self.actual_port = sock.getsockname()[1]
                    break

        return f"http://{self.host}:{self.actual_port}/api/v1/events"

    async def stop(self) -> None:
        if self.runner:
            await self.runner.cleanup()
