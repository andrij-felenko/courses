import json

# (виконується В МОНОЛІТІ або в шарі, що має транзакцію до старої БД)
async def update_profile(db, id: str, patch: dict) -> None:
    """Бізнес-запис і слід у outbox — ОДНА транзакція однієї бази: разом або ніяк."""
    async with db.transaction() as tx:
        await tx.execute(
            "UPDATE users SET data = data || %s WHERE id = %s", (patch, id))
        # слід про зміну — В ТІЙ САМІЙ транзакції. Ось чому це НЕ подвійний запис:
        # якщо UPDATE відкотиться, відкотиться й рядок ящика — атомарно.
        await tx.execute(
            "INSERT INTO outbox(aggregate_id, payload, created_at, sent) "
            "VALUES (%s, %s, now(), false)", (id, json.dumps(patch)))


async def relay_once(db) -> None:
    """Окремий процес-ретранслятор. Крутиться сам собою, у своєму темпі."""
    rows = await db.fetch(
        "SELECT id, aggregate_id, payload FROM outbox "
        "WHERE sent = false ORDER BY id LIMIT 100")   # порядок за id — важливо
    for row in rows:
        try:
            await push_to_profiles_service(row["aggregate_id"], row["payload"])
            # позначаємо обробленим ЛИШЕ після підтвердження від сервісу
            await db.execute("UPDATE outbox SET sent = true WHERE id = %s",
                             (row["id"],))
        except Exception:
            # не вдалося — НЕ чіпаємо sent; наступний прохід повторить рядок.
            # (доставка "щонайменше раз" — приймач має бути ідемпотентним, див. нижче)
            break   # не перестрибуємо через застряглий рядок, бо порядок важливий
