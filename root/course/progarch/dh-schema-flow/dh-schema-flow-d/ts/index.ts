type Raw =
  | { schema: 1; w: number }        // миттєва потужність, Вт
  | { schema: 2; wh: number };      // накопичений лічильник, Вт·год

// Звести будь-яку версію до канону: скільки Вт·год спожито за годину.
// samples — відліки години по порядку; prevMeter — показ лічильника на її початок.
function hourlyWh(samples: Raw[], stepSec: number, prevMeter: number): number {
  const first = samples[0];
  if (first.schema === 1)                               // інтегруємо потужність
    return samples.reduce((s, r) => s + (r as {w:number}).w, 0) * stepSec / 3600;
  const last = samples[samples.length - 1] as { wh: number };
  return last.wh - prevMeter;                            // різниця показів лічильника
}
