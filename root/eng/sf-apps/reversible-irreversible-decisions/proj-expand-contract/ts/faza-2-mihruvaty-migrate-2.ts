// Подвійне читання зі звірянням. Поки trustNew=false — стара авторитетна,
// нова читається лише для звіряння (тінь). Коли доказів досить — прапорець
// перемикають, і авторитетною стає нова.
async function readAmountMinor(db: Db, orderId: number, trustNew: boolean): Promise<bigint> {
  const { rows } = await db.query(
    "SELECT total, amount_minor FROM orders WHERE id = $1", [orderId],
  );
  const { total, amount_minor } = rows[0];
  const oldAsNew = toMinor(String(total));                 // стара → копійки (той самий toMinor)

  if (amount_minor == null) return oldAsNew;               // ще не заповнено

  if (BigInt(amount_minor) !== oldAsNew) {                 // РОЗБІЖНІСТЬ!
    metrics.increment("amount_minor.drift");
    log.error(`drift order=${orderId} old=${oldAsNew} new=${amount_minor}`);
    return oldAsNew;                                        // у сумніві — стара
  }
  return trustNew ? BigInt(amount_minor) : oldAsNew;
}
