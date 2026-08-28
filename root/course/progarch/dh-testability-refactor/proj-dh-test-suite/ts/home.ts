// home.ts — код під тестом (форми v1, без змін)
export interface Reading { celsius: number; ok: boolean; }   // ok=false ⇒ числу не вірити
export interface Config  { threshold: number; }
export type Command = "HEAT" | "IDLE";

export interface Sensor { read(): Reading; }
export interface Heater { on(): void; off(): void; }

export function decide(r: Reading, cfg: Config): Command {    // чиста: значення → значення
  if (!r.ok) return "IDLE";
  return r.celsius < cfg.threshold ? "HEAT" : "IDLE";
}

export function tick(sensor: Sensor, heater: Heater, cfg: Config): void {  // один оберт
  const cmd = decide(sensor.read(), cfg);
  if (cmd === "HEAT") heater.on();
  else heater.off();
}
