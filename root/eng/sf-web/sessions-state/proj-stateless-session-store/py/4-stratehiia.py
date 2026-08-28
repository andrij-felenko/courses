import asyncio
import random

async def mutate_session_with_retry(
    store: StatelessRedisSessionStore,
    session_id: str,
    mutator: Callable[[Dict[str, Any]], Dict[str, Any]],
    max_retries: int = 3,
) -> SessionEnvelope:
    """Виконує модифікацію сесії з автоматичним перечитуванням при версійних конфліктах."""
    for attempt in range(1, max_retries + 1):
        session = await store.get(session_id)
        if not session:
            raise KeyError(f"Cannot mutate non-existent session {session_id}")

        try:
            return await store.update(session_id, session.version, mutator)
        except VersionConflictError:
            if attempt < max_retries:
                backoff = random.uniform(0.005, 0.02) * attempt
                await asyncio.sleep(backoff)
                continue
            raise

    raise RuntimeError(f"CONCURRENCY_ERROR: exceeded max retries for session {session_id}")
