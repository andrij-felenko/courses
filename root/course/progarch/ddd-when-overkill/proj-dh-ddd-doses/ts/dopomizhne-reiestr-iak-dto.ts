// Названі типи: щоб id пристрою й назва кімнати не переплуталися мовчки.
type DeviceId = string & { readonly __brand: "DeviceId" };
type RoomName = string & { readonly __brand: "RoomName" };
type DeviceKind = "heater" | "cooler" | "light" | "sensor" | "lock";

const deviceId = (s: string) => s as DeviceId;    // «розумний» конструктор бренду
const roomName = (s: string) => s as RoomName;

// DTO: названі поля, жодного правила. Знекровлено — і це ПРАВИЛЬНО.
interface Device {
  readonly id: DeviceId;
  readonly room: RoomName;
  readonly kind: DeviceKind;
  readonly name: string;            // як його зве господар: «торшер біля дивана»
}

// Тонкий сервіс: додати, перейменувати, прибрати, вибрати. І все.
class DeviceRegistry {
  constructor(private store: Map<DeviceId, Device>) {}

  register(device: Device): void {
    this.store.set(device.id, device);
  }
  rename(id: DeviceId, name: string): Device {
    const found = this.store.get(id);
    if (!found) throw new Error(`пристрою ${id} немає`);   // не інваріант, а перевірка існування
    const renamed: Device = { ...found, name };           // DTO незмінний — робимо новий
    this.store.set(id, renamed);
    return renamed;
  }
  remove(id: DeviceId): void {
    this.store.delete(id);
  }
  inRoom(room: RoomName): Device[] {
    return [...this.store.values()].filter(d => d.room === room);
  }
}
