import * as fs from "node:fs";

class FileDeviceRepository {                        // за портом DeviceRepository з v2
  private devices: Map<string, Device>;
  constructor(private path = "dh-devices.json") {
    this.devices = this.load();
  }

  private load(): Map<string, Device> {
    try {
      const rows: Device[] = JSON.parse(fs.readFileSync(this.path, "utf8"));
      return new Map(rows.map((d) => [d.id, d]));
    } catch (e: any) {
      if (e.code === "ENOENT") return new Map();    // перший запуск — дім порожній
      throw e;
    }
  }

  save(d: Device): void {
    this.devices.set(d.id, d);                      // онови памʼять…
    this.flush();                                   // …і відразу поклади ВЕСЬ реєстр на диск
  }
  get(id: string): Device | undefined { return this.devices.get(id); }
  all(): Device[] { return [...this.devices.values()]; }

  private flush(): void {                           // атомарний тривкий запис — серце класу
    const tmp = this.path + ".tmp";
    const fd = fs.openSync(tmp, "w");
    fs.writeSync(fd, JSON.stringify([...this.devices.values()]));
    fs.fsyncSync(fd);                               // кеш ОС → на носій, з підтвердженням
    fs.closeSync(fd);
    fs.renameSync(tmp, this.path);                  // атомарна заміна: старий XOR новий
  }
}
