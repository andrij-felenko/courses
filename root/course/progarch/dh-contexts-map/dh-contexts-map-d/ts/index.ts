// Опублікована мова стику: подія пристрою. Належить НЕ споживачам, а кордону.
// Жодних вендорських кластерів і жодних живих доменних об'єктів — тільки факт.
interface DeviceEvent {
  readonly deviceId: string;      // спільний ідентифікатор (див. спільне ядро нижче)
  readonly homeId: string;
  readonly at: string;            // ISO-час, коли факт стався
  readonly payload:
    | { kind: "state"; value: "Locked" | "Unlocked" | "Jammed" | "Unknown" }
    | { kind: "measurement"; unit: string; value: number };
}
