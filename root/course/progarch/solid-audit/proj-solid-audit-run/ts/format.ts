// format.ts — окремий актор (тон), чиста функція. Час беремо ЯВНО, не з Date.now().
export function formatAlarm(zone: string, at: Date): string {
  const hh = String(at.getHours()).padStart(2, "0");
  const mm = String(at.getMinutes()).padStart(2, "0");
  return `Рух у зоні «${zone}» о ${hh}:${mm}`;
}

// policy.ts — стабільне ядро. Залежить ЛИШЕ від портів.
import type { SensorEvent } from "./types";
import type { Notifier, Clock } from "./ports";
import { formatAlarm } from "./format";

export class AlarmPolicy {
  private armed = false;
  constructor(private readonly notifier: Notifier,
              private readonly clock: Clock) {}      // деталі подано ЗЗОВНІ

  arm()    { this.armed = true; }
  disarm() { this.armed = false; }

  async handle(ev: SensorEvent): Promise<void> {
    if (ev.type !== "motion" || !this.armed) return; // політика тривоги…
    if (ev.zone === "pet-safe") return;              // …і тільки вона
    const body = formatAlarm(ev.zone, this.clock.now());
    await this.notifier.send({ to: "owner", body });
  }
}
