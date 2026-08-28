// plugins/markdownExporter.ts — сторонній файл у теці plugins/.
import type { Host, Exporter, Document } from "../contract";

export const PLUGIN_API = 3;        // під яку версію контракту зібрано

class MarkdownExporter implements Exporter {
  readonly extension = "md";
  export(doc: Document): Uint8Array {
    const text = doc.blocks.map(b => `# ${b.title}\n\n${b.body}`).join("\n\n");
    return new TextEncoder().encode(text);
  }
}

export function register(host: Host): void {   // умовлена точка входу
  host.registerExporter(new MarkdownExporter());
}
