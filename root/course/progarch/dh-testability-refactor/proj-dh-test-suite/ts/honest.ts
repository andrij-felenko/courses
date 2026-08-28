// honest.ts — контракт межі, витягнутий у фабрику
import type { Reading } from "./home";

const SENSOR_MIN = -40.0, SENSOR_MAX = 85.0;   // паспортний діапазон давача

export function reading(celsius: number, ok = true): Reading {
  // той самий контракт, що й драйвер: правдиве число ⇒ у паспортних межах
  if (ok && !(celsius >= SENSOR_MIN && celsius <= SENSOR_MAX))
    throw new Error(`${celsius} °C поза −40…85: справжній давач такого з ok=true не дасть`);
  return { celsius, ok };
}
