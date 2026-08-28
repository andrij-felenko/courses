class ExportRegistry {
  private byExt = new Map<string, Exporter>();

  register(e: Exporter): void {             // сюди плагін кладе себе
    this.byExt.set(e.extension, e);
  }

  exportAs(ext: string, doc: Document): Uint8Array {
    const e = this.byExt.get(ext);          // ядро бере плагін за ключем
    if (!e) throw new Error(`немає плагіна для .${ext}`);
    return e.export(doc);                    // і гукає через контракт
  }
}
