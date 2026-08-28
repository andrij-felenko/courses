type RawOrder = Record<string, unknown>;

interface Order {
  id: number;
  total: number;
  customerId: string;      // після міграції — головний ключ
}

function readOrder(raw: RawOrder): Order {
  // ЛІБЕРАЛЬНІСТЬ ДО ФОРМИ, правило 1: відсутнє поле → розумна заглушка, не виняток.
  // Під час міграції customer_id може ще не прийти — падаємо назад на email.
  const customerId =
    typeof raw.customer_id === "string" && raw.customer_id.length > 0
      ? raw.customer_id
      : deriveIdFromEmail(raw.customer_email);

  // ЛІБЕРАЛЬНІСТЬ ДО ФОРМИ, правило 2: незнайомі поля (promo_banner тощо)
  // ми просто НЕ читаємо. Їх наявність нас не обходить і не валить.

  // СУВОРІСТЬ ДО ЗМІСТУ: поля, які нам ТРЕБА, перевіряємо безжально —
  // це вже не сумісність форми, а захист від зіпсованих даних.
  const id = raw.id;
  if (typeof id !== "number" || !Number.isInteger(id) || id <= 0)
    throw new Error(`зіпсований id: ${String(id)}`);

  const total = raw.total;
  if (typeof total !== "number" || total < 0)
    throw new Error(`неможливий total: ${String(total)}`);

  return { id, total, customerId };
}
