// number у JS — float64; для грошей це небезпечно, і саме в цьому причина
// міграції. Тому total тримаємо рядком-десятковим, а копійки рахуємо цілими
// точно, без float: ціла частина · 100 + рівно два знаки дробу.
function toMinor(dec: string): bigint {
  const neg = dec.startsWith("-");                   // знак — окремо, щоб не зіпсувати дріб
  const [whole, frac = ""] = dec.replace("-", "").split(".");
  const cents = (frac + "00").slice(0, 2);           // рівно 2 знаки копійок
  const v = BigInt(whole) * 100n + BigInt(cents);
  return neg ? -v : v;
}

// Подвійний запис: обидві форми в одному операторі, узгоджено.
async function createOrder(db: Db, customerId: number, total: string /* "123.45" */) {
  await db.query(
    `INSERT INTO orders (customer_id, total, amount_minor)
     VALUES ($1, $2, $3)`,
    [customerId, total, toMinor(total)],
  );
}
