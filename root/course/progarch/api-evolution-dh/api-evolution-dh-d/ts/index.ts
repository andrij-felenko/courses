type DeviceStateDTO = {
  // старе поле — лишаємо байт-у-байт, поки його хтось читає
  tempC: number;
  // нове поле — канонічне джерело правди
  temperature: { value: number; unit: "C" | "F" };
  at: number;
};

function buildState(d: Device): DeviceStateDTO {
  const temperature = d.temperature;                 // єдина правда
  return {
    temperature,
    tempC: toCelsius(temperature),                   // старе — ПОХІДНЕ від нового
    at: d.lastReadingAt,
  };
}
