// --- registry.ts: ЯДРО. Пишеться раз, на формати не відкривається ---
export type Row = Record<string, unknown>;

// Контракт розширення (порт). Ядро володіє ним; варіанти його реалізують.
export interface Exporter {
  readonly format: string;               // ключ, під яким варіант відповідає
  export(rows: Row[]): string;           // єдина операція контракту
}

const registry = new Map<string, Exporter>();

// Точка самозапису. Її кличе КОЖЕН варіант — з власного файлу.
export function register(exporter: Exporter): void {
  if (registry.has(exporter.format))
    throw new Error(`формат '${exporter.format}' вже зайнято`);
  registry.set(exporter.format, exporter);
}

// Диспетчер: знайти реалізацію за форматом і делегувати. Жодного варіанта не знає.
export function exportReport(format: string, rows: Row[]): string {
  const exporter = registry.get(format);
  if (!exporter) throw new Error(`немає експортера для '${format}'`);
  return exporter.export(rows);          // поліморфний виклик
}
