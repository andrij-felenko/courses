import { pathToFileURL } from "node:url";
import { readdir } from "node:fs/promises";
import * as path from "node:path";
import { HOST_API, type Exporter, type Host } from "./contract";

// проста заміна логера — у реальному ядрі це ваш logger
const log = console;

class ExportRegistry {
  // Серце ядра: сюди плагіни складають себе, звідси ядро їх бере.
  private byExt = new Map<string, Exporter>();

  register(e: Exporter): void {
    this.byExt.set(e.extension, e);
  }

  exportAs(ext: string, doc: Document): Uint8Array {
    const e = this.byExt.get(ext);
    if (!e) throw new Error(`немає плагіна для .${ext}`);
    return e.export(doc);
  }
}

class HostImpl implements Host {
  // Єдине вікно, яке ядро дає плагінові. Плагін дотягується до ядра
  // ТІЛЬКИ через методи цього об'єкта — і нікуди більше.
  constructor(private readonly registry: ExportRegistry) {}

  registerExporter(e: Exporter): void {
    this.registry.register(e);
  }
}
