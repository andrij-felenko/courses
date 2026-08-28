type Temperature = { value: number; unit: "C" | "F" };

interface Device {
  id: string;
  temperature: Temperature;   // канонічне джерело правди
  lastReadingAtMs: number;    // канонічне: epoch у мілісекундах
}

// DTO на дроті: нові поля канонічні, старі — суто похідні.
interface DeviceStateDTO {
  temperature: Temperature;   // нове
  atMs: number;               // нове
  tempC: number;              // старе — ПОХІДНЕ
  at: number;                 // старе — ПОХІДНЕ (секунди)
}

const toCelsius = (t: Temperature): number =>
  t.unit === "C" ? t.value : ((t.value - 32) * 5) / 9;

const round1 = (x: number): number => Math.round(x * 10) / 10;

function buildDeviceState(d: Device): DeviceStateDTO {
  return {
    temperature: d.temperature,                  // єдина правда
    atMs: d.lastReadingAtMs,                      // єдина правда
    tempC: round1(toCelsius(d.temperature)),      // ← виводимо, не рахуємо окремо
    at: Math.floor(d.lastReadingAtMs / 1000),     // ← виводимо
  };
}
