// --- exporters/csv.ts: цілком самодостатній, залежить лише від контракту ---
import { Exporter, Row, register } from "../registry";

class CsvExporter implements Exporter {
  readonly format = "csv";
  export(rows: Row[]): string {
    if (rows.length === 0) return "";
    const cols = Object.keys(rows[0]);
    const head = cols.join(",");
    const body = rows.map(r => cols.map(c => String(r[c])).join(",")).join("\n");
    return `${head}\n${body}`;
  }
}

register(new CsvExporter());     // ← самозапис при завантаженні модуля
