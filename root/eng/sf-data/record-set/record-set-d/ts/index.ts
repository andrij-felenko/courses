// Набір рядків, що описує сам себе: колонки з іменами й типами + значення.
type Column = { name: string; type: "int" | "text" | "real" | "time" };
type Cell = string | number | null;            // null — це саме NULL, окремий стан
type RecordSet = { columns: Column[]; rows: Cell[][] };

// Той самий експортер для будь-якого запиту: він читає схему, а не знає її наперед.
function exportCsv(rs: RecordSet): string {
  const quote = (s: string) =>
    /[",\n]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;

  const head = rs.columns.map((c) => quote(c.name)).join(",");
  const body = rs.rows.map((row) =>
    row.map((v) => (v === null ? "" : quote(String(v)))).join(","),
  );
  return [head, ...body].join("\n");
}
