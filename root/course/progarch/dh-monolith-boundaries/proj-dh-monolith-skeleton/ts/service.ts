// control/service.ts — команда й розсилка події в ОДНІЙ транзакції
import type { Bus } from "../ids";
export class Control {
  constructor(private readonly repo: DeviceRepo, private readonly bus: Bus) {}
  apply(cmd: Command): void {
    this.repo.tx((tx) => {                          // ← одна транзакція на всю операцію
      const device = this.repo.apply(cmd, tx);      // приватна нутрощі: пише в схему control
      this.bus.publish({                            // підписники біжать ТУТ-ТАКИ, у цій tx
        kind: "state", deviceId: device.id, homeId: device.homeId,
        at: Date.now(), value: device.state,
      });
    });   // коллбек завершився без винятку → COMMIT; кинув будь-хто всередині → ROLLBACK усього
  }
}
export function makeControl(schema: Schema, bus: Bus): Control {
  return new Control(new DeviceRepo(schema), bus);
}
