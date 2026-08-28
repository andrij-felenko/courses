// telemetry/contract.ts — ПУБЛІЧНЕ: те, що бачать сусіди
import type { DeviceId } from "../ids";
export interface Reading { deviceId: DeviceId; value: number; at: number; }

// telemetry/store.ts — ПРИВАТНЕ: лише цей модуль торкається схеми telemetry
import type { DeviceId } from "../ids";
import type { Reading } from "./contract";
import type { Schema } from "../ids/db";          // дескриптор ЛИШЕ однієї схеми
export class ReadingStore {                        // з index не реекспортовано → зовні не існує
  constructor(private readonly s: Schema) {
    s.exec(`CREATE TABLE IF NOT EXISTS telemetry.reading(
              device_id TEXT, value DOUBLE PRECISION, at BIGINT)`);
  }
  put(r: Reading): void {
    this.s.exec(`INSERT INTO telemetry.reading(device_id, value, at) VALUES ($1,$2,$3)`,
                [r.deviceId, r.value, r.at]);
  }
  last(id: DeviceId): Reading | null {
    const row = this.s.queryOne(
      `SELECT value, at FROM telemetry.reading WHERE device_id=$1 ORDER BY at DESC LIMIT 1`, [id]);
    return row ? { deviceId: id, value: row.value, at: row.at } : null;
  }
}

// telemetry/service.ts — реалізація фасаду (клас приватний; назовні йде лише інтерфейс)
import type { DeviceId, DeviceEvent } from "../ids";
import type { Reading } from "./contract";
import type { Schema } from "../ids/db";
import { ReadingStore } from "./store";
export interface Telemetry {                        // ← ФАСАД: усе, що бачать сусіди
  record(e: DeviceEvent): void;                     // підписник шини
  lastReading(id: DeviceId): Reading | null;
}
class TelemetryService implements Telemetry {
  constructor(private readonly store: ReadingStore) {}
  record(e: DeviceEvent): void {
    if (e.kind === "state") this.store.put({ deviceId: e.deviceId, value: e.value, at: e.at });
  }
  lastReading(id: DeviceId): Reading | null { return this.store.last(id); }
}
export function makeTelemetry(schema: Schema): Telemetry {  // фабрика в'яже приватний стор зі схемою
  return new TelemetryService(new ReadingStore(schema));
}

// telemetry/index.ts — БАР'ЄР: єдині двері модуля
export type { Reading } from "./contract";
export type { Telemetry } from "./service";
export { makeTelemetry } from "./service";
// ReadingStore, TelemetryService, схема — НЕ реекспортовано: для сусідів їх нема
