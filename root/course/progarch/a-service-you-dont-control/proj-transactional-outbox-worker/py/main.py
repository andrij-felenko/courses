"""
Точка входу: демонстрація роботи Transactional Outbox, хаос-тестування та самозцілення.
"""

import asyncio
import time

from http_client import IdempotentClient
from mock_server import MockPartnerServer
from models import OutboxStatus, WorkerConfig
from repository import OutboxRepository
from worker import OutboxWorker


async def run_simulation():
    print("=" * 75)
    print(" ТРАНЗАКЦІЙНИЙ АУТБОКС (TRANSACTIONAL OUTBOX) НА PYTHON (asyncio + asyncpg) ")
    print("=" * 75)

    mock_server = MockPartnerServer(host="127.0.0.1", port=0)
    mock_server.fatal_event_types.add("InvalidOrderFormat")
    mock_server.drop_response_keys.add("idem-order-002")
    target_url = await mock_server.start()
    print(f"[*] Mock Partner API запущено: {target_url}")

    repo = OutboxRepository(pg_pool=None)
    await repo.init_schema()
    http_client = IdempotentClient(timeout_s=1.5)

    print("\n--- ЕТАП 1: Атомарна фіксація намірів у таблиці Outbox (Dual-Write Protection) ---")

    for i in range(1, 6):
        await repo.save_within_transaction(
            aggregate_type="Order",
            aggregate_id=f"order-{i:03d}",
            event_type="OrderPlaced",
            payload={"amount": 100 * i, "currency": "UAH", "customer": f"user_{i}"},
            idempotency_key=f"idem-order-{i:03d}",
            max_attempts=6,
        )

    await repo.save_within_transaction(
        aggregate_type="Order",
        aggregate_id="order-poison-999",
        event_type="InvalidOrderFormat",
        payload={"corrupted": True},
        idempotency_key="idem-order-poison-999",
        max_attempts=3,
    )

    for i in range(7, 11):
        await repo.save_within_transaction(
            aggregate_type="Payment",
            aggregate_id=f"pay-{i:03d}",
            event_type="PaymentRequested",
            payload={"sum": 250 * i, "gateway": "AcquirerX"},
            idempotency_key=f"idem-pay-{i:03d}",
            max_attempts=6,
        )

    initial_stats = await repo.get_stats()
    print(f"[*] Створено подій у статусі PENDING: {initial_stats['PENDING']}")

    print("\n--- ЕТАП 2: Конкурентна вибірка пачок (SELECT ... FOR UPDATE SKIP LOCKED) ---")
    worker_cfg = WorkerConfig(
        batch_size=3,
        poll_interval_s=0.1,
        max_concurrent_tasks=3,
        lease_timeout_s=2.0,
        base_delay_s=0.08,
        max_delay_s=0.3,
    )

    stop_event = asyncio.Event()
    worker1 = OutboxWorker("Worker-1", repo, http_client, target_url, worker_cfg)
    worker2 = OutboxWorker("Worker-2", repo, http_client, target_url, worker_cfg)

    mock_server.chaos_fail_rate = 0.5
    mock_server.chaos_latency_s = 0.03
    print("[!] Зовнішній сервіс деградував: 50% збоїв 503, затримка 30 мс.")

    w1_task = asyncio.create_task(worker1.run(stop_event))
    w2_task = asyncio.create_task(worker2.run(stop_event))
    print("[*] Два паралельні воркери (Worker-1 і Worker-2) успішно активували опитування черги.")

    print("\n--- ЕТАП 3: Хаос-інжекція (503 помилки + мережеві затримки) та Full Jitter Backoff ---")
    await asyncio.sleep(0.6)
    chaos_stats = await repo.get_stats()
    print(f"[*] Проміжний стан під час збоїв: {chaos_stats}")

    print("\n--- ЕТАП 4: Відновлення зовнішньої служби та гарантована доставка (At-Least-Once) ---")
    mock_server.chaos_fail_rate = 0.0
    mock_server.chaos_latency_s = 0.0
    print("[+] Партнерський сервіс повністю відновив працездатність.")

    for _ in range(30):
        stats = await repo.get_stats()
        if stats[OutboxStatus.PENDING.value] == 0 and stats[OutboxStatus.PROCESSING.value] == 0:
            break
        await asyncio.sleep(0.15)

    stop_event.set()
    await asyncio.gather(w1_task, w2_task)
    await http_client.close()

    print("\n" + "=" * 75)
    print(" РЕЗУЛЬТАТИ ВЕРИФІКАЦІЇ ТА ДЕМОНСТРАЦІЇ ")
    print("=" * 75)

    final_stats = await repo.get_stats()
    print(f"Розподіл статусів подій Outbox:")
    print(f"  - PROCESSED (успішно доставлено):   {final_stats[OutboxStatus.PROCESSED.value]}")
    print(f"  - DEAD_LETTER (ізольовано в DLQ):    {final_stats[OutboxStatus.DEAD_LETTER.value]}")
    print(f"  - PENDING (залишилось у черзі):      {final_stats[OutboxStatus.PENDING.value]}")
    print(f"  - PROCESSING (завислих у роботі):    {final_stats[OutboxStatus.PROCESSING.value]}")

    print(f"\nМетрики тестового сервера:")
    print(f"  - Всього прийнято HTTP-запитів:     {mock_server.call_count}")
    print(f"  - Унікальних операцій виконано:     {len(mock_server.received_keys)}")
    print(f"  - Відсічено дублікатів по ключу:    {mock_server.duplicate_count}")

    assert final_stats[OutboxStatus.PROCESSED.value] == 9, (
        f"Очікувалось 9 успішних подій, отримано {final_stats[OutboxStatus.PROCESSED.value]}"
    )
    assert final_stats[OutboxStatus.DEAD_LETTER.value] == 1, (
        f"Очікувалось 1 повідомлення в DLQ, отримано {final_stats[OutboxStatus.DEAD_LETTER.value]}"
    )
    assert len(mock_server.received_keys) == 9, "Кількість унікальних мутацій не збігається!"
    assert mock_server.duplicate_count >= 1, "Має бути зафіксовано щонайменше 1 дублюючий запит з ідемпотентним захистом!"

    print("\n[V] ВСІ АРХІТЕКТУРНІ ІНВАРІАНТИ ВИКОНАНО:")
    print("    1. Проблему Dual-Write усунуто: наміри збережено локально до відправки.")
    print("    2. Конкурентна вибірка SKIP LOCKED усунула гонки між воркерами.")
    print("    3. Full Jitter бекоф запобіг шторму повторних запитів.")
    print("    4. Idempotency-Key унеможливив дублювання мутацій у зовнішньому API.")
    print("    5. Отруйне повідомлення надійно ізольовано в Dead Letter Queue.")

    await mock_server.stop()


def main():
    asyncio.run(run_simulation())


if __name__ == "__main__":
    main()
