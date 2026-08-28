// --- exporters/json.ts ---
import { Exporter, Row, register } from "../registry";

class JsonExporter implements Exporter {
  readonly format = "json";
  export(rows: Row[]): string {
    return JSON.stringify(rows, null, 2);
  }
}

register(new JsonExporter());
