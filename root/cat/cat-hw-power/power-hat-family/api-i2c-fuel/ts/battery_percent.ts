// battery_percent.ts — те саме для сервісного демона на Node.
//   npm i i2c-bus     (bindings до /dev/i2c-*)
import { openSync } from "i2c-bus";

const INA219 = 0x40; // 7-бітна адреса паливоміра
const REG_V  = 0x02; // Bus Voltage

function readVoltage(): number {
  const bus = openSync(1); // /dev/i2c-1
  const raw = bus.readWordSync(INA219, REG_V);
  bus.closeSync();
  const be = ((raw << 8) | (raw >> 8)) & 0xffff; // → big-endian
  return (be >> 3) * 0.004;                        // 13 біт · 4 мВ
}

// Та сама груба крива розряду літію (напруга → відсоток).
const CURVE: [number, number][] = [
  [4.2, 100], [4.1, 90], [4.0, 80], [3.9, 65],
  [3.8, 50],  [3.7, 40], [3.6, 25], [3.5, 15],
  [3.4, 8],   [3.3, 3],  [3.0, 0],
];

function voltageToPercent(v: number): number {
  if (v >= CURVE[0][0]) return 100;
  if (v <= CURVE[CURVE.length - 1][0]) return 0;
  for (let i = 0; i < CURVE.length - 1; i++) {
    const [vHi, pHi] = CURVE[i];
    const [vLo, pLo] = CURVE[i + 1];
    if (v >= vLo && v <= vHi) {
      const k = (v - vLo) / (vHi - vLo); // інтерполяція в сегменті
      return Math.round(pLo + k * (pHi - pLo));
    }
  }
  return 0;
}

const SHUTDOWN_AT = 10;
const v = readVoltage();
const pct = voltageToPercent(v);
console.log(`${v.toFixed(3)} В  →  ~${pct}%`);
if (pct <= SHUTDOWN_AT) {
  console.log("Низький заряд — коректне вимкнення.");
  // import { execSync } from "child_process";
  // execSync("sudo shutdown -h now");
}
