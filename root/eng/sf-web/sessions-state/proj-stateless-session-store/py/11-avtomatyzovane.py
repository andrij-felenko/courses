import asyncio
import redis.asyncio as aioredis
from session_store import StatelessRedisSessionStore, mutate_session_with_retry

async def run_concurrency_test():
    redis = aioredis.from_url("redis://localhost:6379")
    store = StatelessRedisSessionStore(redis)

    session = await store.create({"items": []})
    session_id = session.id

    concurrent_requests = 20

    async def append_item(index: int):
        await mutate_session_with_retry(
            store,
            session_id,
            lambda data: {**data, "items": data.get("items", []) + [f"item_{index}"]},
        )

    # Запускаємо 20 паралельних корутин
    await asyncio.gather(*(append_item(i + 1) for i in range(concurrent_requests)))

    final_session = await store.get(session_id)
    items = final_session.data.get("items", []) if final_session else []

    print(f"Очікувалось товарів: ${concurrent_requests}, фактично в сесії: ${len(items)}")
    print(f"Фінальна версія документа: ${final_session.version if final_session else 'None'}")

    assert len(items) == concurrent_requests, "Виявлено втрату оновлень!"
    print("ТЕСТ ПРОЙДЕНО: усі паралельні модифікації збережено успішно!")

    await store.destroy(session_id)
    await redis.aclose()

if __name__ == "__main__":
    asyncio.run(run_concurrency_test())
