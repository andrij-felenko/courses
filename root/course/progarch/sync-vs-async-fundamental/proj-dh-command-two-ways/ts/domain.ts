// domain.ts — спільний словник обох шляхів
export type HomeId = string;
export type CommandId = string;
export type LockState = "locked" | "unlocked" | "unknown";

export interface LockCommand {
  commandId: CommandId;
  home: HomeId;
  cmd: "lock";
}

// Дві помилки хаба, які нам ВАЖЛИВО розрізняти нагорі:
export class HubOffline extends Error {}   // хаба нема на зв'язку — команду нема куди подіти
export class HubTimeout extends Error {}   // хаб мовчить — ми не знаємо, клацнув замок чи ні

// Контракт до фізичного хаба. Обидва шляхи кличуть рівно це.
// Може повернути стан, кинути HubOffline — або зависнути (тоді спрацює наш таймаут).
export interface Hub {
  send(home: HomeId, cmd: { cmd: "lock" }): Promise<{ state: LockState }>;
}
