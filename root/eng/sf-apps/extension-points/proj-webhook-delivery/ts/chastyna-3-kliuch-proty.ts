import { randomUUID } from "node:crypto";

// Одиниця роботи в черзі доставки. Ключ народжується РАЗ, при створенні,
// і НЕ змінюється, скільки б спроб не було.
interface DeliveryJob {
  deliveryId: string;   // ← сталий ключ ідемпотентності на всі повтори
  url: string;
  payload: object;
  attempt: number;
}

function newDeliveryJob(url: string, payload: object): DeliveryJob {
  return { deliveryId: randomUUID(), url, payload, attempt: 0 };
  //                   ^^^^^^^^^^^^ один раз — і назавжди для цієї доставки
}

// ── Бік ОДЕРЖУВАЧА: атомарний claim ключа перед роботою ──
async function handleIncoming(key: string, body: string, db: DB): Promise<number> {
  // Атомарно: вставити ключ. Уже був → 0 рядків → це ДУБЛІКАТ.
  const inserted = await db.query(
    `INSERT INTO processed_webhooks(key) VALUES ($1)
       ON CONFLICT (key) DO NOTHING`,
    [key],
  );
  if (inserted.rowCount === 0) {
    return 200;                 // вже бачили цей ключ → нічого не робимо, кажемо OK
  }
  doTheWork(body);              // побічний ефект — РІВНО раз
  return 200;
}
