// ids/types.ts — спільний словник: марковані примітиви, щоб не сплутати ідентифікатори
export type DeviceId = string & { readonly __brand: "DeviceId" };
export type HomeId   = string & { readonly __brand: "HomeId" };

// ids/events.ts — ДРОТОВИЙ факт: ані живих агрегатів, ані вендорських типів
import type { DeviceId, HomeId } from "./types";
export interface DeviceEvent {
  kind: "state" | "added" | "removed";
  deviceId: DeviceId;
  homeId: HomeId;
  at: number;      // epoch-мілісекунди — примітив, не Date якоїсь бібліотеки
  value: number;
}

// ids/bus.ts — внутрішньопроцесна шина: СИНХРОННА диспетчеризація в тій самій транзакції
import type { DeviceEvent } from "./events";
export type Subscriber = (e: DeviceEvent) => void;

export class Bus {
  private subs: Subscriber[] = [];
  subscribe(handler: Subscriber): void { this.subs.push(handler); }
  publish(event: DeviceEvent): void {
    for (const handler of this.subs) handler(event);   // по черзі, ТУТ-ТАКИ, у tx продюсера
  }                                                    // виняток підписника ЛЕТИТЬ УГОРУ
}

// ids/index.ts — БАР'ЄР спільного ядра
export type { DeviceId, HomeId } from "./types";
export type { DeviceEvent } from "./events";
export { Bus } from "./bus";
export type { Subscriber } from "./bus";
