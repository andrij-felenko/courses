// Довідники — константи НАШОГО коду. Ззовні приходить лише ключ.
const FILTERS = {
  status:   "status = $",
  customer: "customer_id = $",
  minTotal: "total_cents >= $",
} as const;
const SORTS = { id: "id", total: "total_cents", date: "updated_at" } as const;

type Criteria = Partial<Record<keyof typeof FILTERS, unknown>>;

async search(
  where: Criteria,
  sortBy: keyof typeof SORTS = "id",
  desc = false,
  limit = 100,
): Promise<OrderRow[]> {
  const parts: string[] = [];
  const values: unknown[] = [];
  for (const key of Object.keys(FILTERS) as (keyof typeof FILTERS)[]) {
    if (where[key] === undefined) continue;
    values.push(where[key]);
    parts.push(FILTERS[key] + values.length);      // «status = $1»
  }
  const clause = parts.length ? `WHERE ${parts.join(" AND ")}` : "";
  const order = SORTS[sortBy];                     // типи зникають при запуску —
  if (!order) throw new Error("невідома колонка сортування");   // перевіряємо НАЖИВО
  values.push(limit);                              // межа — теж значення, теж параметр
  const sql = `SELECT ${COLS} FROM orders ${clause} ` +
              `ORDER BY ${order} ${desc ? "DESC" : "ASC"} LIMIT $${values.length}`;
  return (await this.db.query(sql, values)).rows;
}
