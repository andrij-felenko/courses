// Плаский пакунок: самі поля, нуль поведінки, версія формату. Скроєний на дріт.
interface DeviceDTO {
  v: 1;                            // версія формату — знадобиться в кінці
  id: string;
  type: string; room: string; state: string;
  brightness: number; lastSeen: number;
}

class Hub {
  // ... register / get / ids — як вище ...

  // ГРУБА межа: один метод збирає ВЕСЬ реєстр у пакунок.
  // Усі геттери тут дарові — Device лежить у тому самому процесі.
  snapshot(): DeviceDTO[] {
    const out: DeviceDTO[] = [];
    for (const d of this.devices.values())
      out.push({ v: 1, id: d.id,
        type: d.type(), room: d.room(), state: d.state(),
        brightness: d.brightness(), lastSeen: d.lastSeen() });
    return out;
  }
}
