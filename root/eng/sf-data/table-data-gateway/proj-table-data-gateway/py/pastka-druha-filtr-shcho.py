# Довідники — константи НАШОГО коду. Ззовні приходить лише ключ.
FILTERS = {
    "status":    "status = %s",
    "customer":  "customer_id = %s",
    "min_total": "total_cents >= %s",
}
SORTS = {"id": "id", "total": "total_cents", "date": "updated_at"}


def search(self, where, sort_by="id", desc=False, limit=100):
    parts, values = [], []
    for key, fragment in FILTERS.items():          # порядок задає НАШ довідник
        if key in where:
            parts.append(fragment)
            values.append(where[key])
    clause = "WHERE " + " AND ".join(parts) if parts else ""
    order = SORTS[sort_by]                         # ключа немає — KeyError, і добре
    direction = "DESC" if desc else "ASC"
    values.append(limit)                           # межа — теж значення, теж параметр
    sql = (f"SELECT {COLS} FROM orders {clause} "
           f"ORDER BY {order} {direction} LIMIT %s")
    with self.db.cursor(row_factory=dict_row) as cur:
        cur.execute(sql, values)
        return cur.fetchall()
