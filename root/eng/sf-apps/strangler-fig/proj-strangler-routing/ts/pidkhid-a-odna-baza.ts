// (виконується В МОНОЛІТІ або в шарі, що має транзакцію до старої БД)
// Бізнес-запис і слід у outbox — ОДНА транзакція однієї бази: разом або ніяк.
async function updateProfile(db: Db, id: string, patch: object): Promise<void> {
  await db.transaction(async tx => {
    await tx.query("UPDATE users SET data = data || $2 WHERE id = $1",
                   [id, patch]);
    // слід про зміну — В ТІЙ САМІЙ транзакції. Ось чому це НЕ подвійний запис:
    // якщо UPDATE відкотиться, відкотиться й рядок ящика — атомарно.
    await tx.query(
      "INSERT INTO outbox(aggregate_id, payload, created_at, sent) " +
      "VALUES ($1, $2, now(), false)", [id, JSON.stringify(patch)]);
  });
}

// Окремий процес-ретранслятор. Крутиться сам собою, у своєму темпі.
async function relayOnce(db: Db): Promise<void> {
  const rows = await db.query(
    "SELECT id, aggregate_id, payload FROM outbox " +
    "WHERE sent = false ORDER BY id LIMIT 100");   // порядок за id — важливо
  for (const row of rows) {
    try {
      await pushToProfilesService(row.aggregate_id, row.payload);  // у нову базу
      // позначаємо обробленим ЛИШЕ після підтвердження від сервісу
      await db.query("UPDATE outbox SET sent = true WHERE id = $1", [row.id]);
    } catch {
      // не вдалося — НЕ чіпаємо sent; наступний прохід повторить цей самий рядок.
      // (доставка "щонайменше раз" — тому приймач має бути ідемпотентним, див. нижче)
      break;   // не перестрибуємо через застряглий рядок, бо порядок важливий
    }
  }
}
