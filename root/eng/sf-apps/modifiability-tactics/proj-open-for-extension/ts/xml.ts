// --- exporters/xml.ts: НОВИЙ файл. Більше не чіпаємо НІЧОГО ---
import { Exporter, Row, register } from "../registry";

class XmlExporter implements Exporter {
  readonly format = "xml";
  export(rows: Row[]): string {
    const cell = (k: string, v: unknown) => `<${k}>${String(v)}</${k}>`;
    const row  = (r: Row) =>
      `  <row>${Object.entries(r).map(([k, v]) => cell(k, v)).join("")}</row>`;
    return `<rows>\n${rows.map(row).join("\n")}\n</rows>`;
  }
}

register(new XmlExporter());
