// КОНТЕКСТ КЕРУВАННЯ (ядро): пристрій — жива керована річ
namespace Control {
  export interface Device {
    readonly id: DeviceId;
    readonly kind: "lock" | "lamp" | "sensor";
    readonly capabilities: ReadonlySet<string>;   // що саме вміє
    state: DeviceState;                            // яким командуємо
    readonly room: RoomId;
    // тут живуть інваріанти; змінюється з новим протоколом чи залізом
  }
}

// КОНТЕКСТ ТЕЛЕМЕТРІЇ: пристрій — лише джерело ряду вимірів
namespace Telemetry {
  export interface Device {
    readonly sourceId: SourceId;
    readonly unit: string;              // "°C", "lux", ...
    readonly retentionDays: number;
    // ні стану, ні життєвого циклу; змінюється з retention/аналітикою
  }
}

// КОНТЕКСТ БІЛІНГУ (загальне): пристрій — рядок тарифу
namespace Billing {
  export interface Device {
    readonly homeId: HomeId;
    readonly countsAgainstPlan: boolean;
    readonly activeSince: string;       // ISO-дата
    // байдуже, лампа то чи замок; змінюється з цінами й планами
  }
}
