// device-lifecycle.ts — АГРЕГАТ життєвого циклу. Стан, таблиця й події — в одному місці.
export type DeviceStatus = "new" | "online" | "offline" | "retired";
export type Command = "commission" | "markOffline" | "markOnline" | "retire";

// ── Єдине джерело правди: (стан, команда) → новий стан. Лише переходи, що МІНЯЮТЬ стан.
const TRANSITIONS: ReadonlyMap<string, DeviceStatus> = new Map([
  ["new|commission",     "online"],
  ["online|markOffline", "offline"],
  ["offline|markOnline", "online"],
  ["online|retire",      "retired"],
  ["offline|retire",     "retired"],
]);

// «Уже в цільовому стані» → тихий no-op (без переходу й БЕЗ події).
// commission СЮДИ не входить: другий commission — це помилка, а не повтор.
const IDEMPOTENT: ReadonlyMap<Command, DeviceStatus> = new Map([
  ["markOffline", "offline"],
  ["markOnline",  "online"],
  ["retire",      "retired"],
]);
const key = (s: DeviceStatus, c: Command) => `${s}|${c}`;

// ── Доменні події — незмінні факти «щось СТАЛОСЯ», сформульовані мовою дому.
export type DomainEvent =
  | { kind: "DeviceCommissioned"; deviceId: string; homeId: string; at: number }
  | { kind: "DeviceWentOffline";  deviceId: string; at: number }
  | { kind: "DeviceReconnected";  deviceId: string; at: number }
  | { kind: "DeviceRetired";      deviceId: string; at: number };

export class DomainError extends Error {}

export class Device {
  private status: DeviceStatus = "new";
  private homeId: string | null = null;
  private readonly events: DomainEvent[] = [];      // зібрані, ще не опубліковані

  constructor(readonly id: string) {}

  // Ядро: єдиний прохід крізь таблицю. Тут і вартовий, і запис події.
  // make() будує подію ЛИШЕ при реальному переході — для no-op не викликається.
  private apply(cmd: Command, make: () => DomainEvent): void {
    if (IDEMPOTENT.get(cmd) === this.status) return;          // уже там — тихо, без події
    const next = TRANSITIONS.get(key(this.status, cmd));
    if (next === undefined)
      throw new DomainError(`з «${this.status}» команда «${cmd}» неможлива`);
    this.status = next;
    this.events.push(make());                                 // подія на КОЖНОМУ переході
  }

  commission(homeId: string, at = Date.now()): void {
    this.apply("commission",
      () => ({ kind: "DeviceCommissioned", deviceId: this.id, homeId, at }));
    this.homeId = homeId;                             // досяжне лише при реальному переході
  }
  markOffline(at = Date.now()): void {
    this.apply("markOffline", () => ({ kind: "DeviceWentOffline", deviceId: this.id, at }));
  }
  markOnline(at = Date.now()): void {
    this.apply("markOnline", () => ({ kind: "DeviceReconnected", deviceId: this.id, at }));
  }
  retire(at = Date.now()): void {
    this.apply("retire", () => ({ kind: "DeviceRetired", deviceId: this.id, at }));
  }

  get state(): DeviceStatus { return this.status; }
  pullEvents(): DomainEvent[] { return this.events.splice(0); }  // забрати й спорожнити
}
