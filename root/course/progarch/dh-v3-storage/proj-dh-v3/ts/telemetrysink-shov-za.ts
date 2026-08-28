interface TelemetrySink {             // ВІДКЛАДЕНИЙ ШОВ на місці майбутнього розлому
  append(deviceId: string, ts: number, value: number): void;
}

class SqliteTelemetrySink implements TelemetrySink {   // реалізація ЗАРАЗ, тривкість послаблена
  constructor(private db: DatabaseSync) {}             // відкрито з synchronous=NORMAL
  append(deviceId: string, ts: number, value: number): void {
    this.db.prepare("INSERT INTO measurement(device_id, ts, value) VALUES(?,?,?)")
      .run(deviceId, ts, value);
  }
}

// коли масштаб зросте, СЮДИ стане LsmTelemetrySink за ТИМ САМИМ портом — реєстру не чіпаючи
