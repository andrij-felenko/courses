type Row = Record<string, unknown>;

// ЯДРО, яке доводиться відкривати на КОЖЕН новий формат
function exportReport(format: string, rows: Row[]): string {
  switch (format) {
    case "csv":  return toCsv(rows);
    case "json": return JSON.stringify(rows, null, 2);
    // ← новий формат = нова гілка ТУТ, у вже робочому ядрі
    default: throw new Error(`невідомий формат: ${format}`);
  }
}
