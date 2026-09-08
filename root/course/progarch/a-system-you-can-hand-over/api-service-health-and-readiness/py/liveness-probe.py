import asyncio
import signal
import sys
from fastapi import FastAPI, Response, status

app = FastAPI(title="OrderProcessingService")

# Атомарні прапорці життєвого циклу процесу
is_ready = True
is_alive = True
in_flight_requests = 0
shutdown_event = asyncio.Event()

@app.get("/healthz")
async def liveness_probe():
    # Liveness залишається 200 OK доти, доки працює цикл подій
    if not is_alive:
        return Response(
            content='{"status": "fail", "reason": "Process is terminating"}',
            media_type="application/health+json",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    return Response(
        content='{"status": "pass"}',
        media_type="application/health+json",
        status_code=status.HTTP_200_OK
    )

@app.get("/ready")
async def readiness_probe():
    # Readiness негайно сигналізує 503, коли розпочато виведення з експлуатації
    if not is_ready:
        return Response(
            content='{"status": "fail", "reason": "Draining traffic"}',
            media_type="application/health+json",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    return Response(
        content='{"status": "pass"}',
        media_type="application/health+json",
        status_code=status.HTTP_200_OK
    )

@app.post("/api/v1/orders")
async def create_order():
    global in_flight_requests
    if not is_ready:
        return Response(
            content='{"error": "Server is shutting down"}',
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    
    in_flight_requests += 1
    try:
        # Емуляція виконання тривалої бізнес-транзакції
        await asyncio.sleep(2.0)
        return {"status": "created", "order_id": "ORD-98421"}
    finally:
        in_flight_requests -= 1

async def handle_sigterm(sig):
    global is_ready, is_alive
    # Крок 1: Негайне виведення з ротації балансувальника
    is_ready = False

    # Крок 2: Пауза для оновлення мережевих маршрутів оркестратора
    await asyncio.sleep(5.0)

    # Крок 3: Очікування завершення активних запитів (таймаут 15 с)
    drain_timeout = 15.0
    elapsed = 0.0
    while in_flight_requests > 0 and elapsed < drain_timeout:
        await asyncio.sleep(0.5)
        elapsed += 0.5

    # Крок 4: Фінальна зупинка - переведення liveness перед виходом
    is_alive = False
    shutdown_event.set()
