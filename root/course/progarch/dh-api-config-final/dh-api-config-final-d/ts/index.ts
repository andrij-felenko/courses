// Публічна поверхня v1: тільки ДОДАЄМО, ніколи не переінакшуємо.
// Одне джерело правди — доменний Device; старе виводимо з нового.
type DeviceDTO = {
  id: string;                                        // формат опублікований — заморожений
  temperature: { value: number; unit: "C" | "F" };  // канон
  tempC: number;                                     // legacy: ПОХІДНЕ, живе поки читають
  power?: { watts: number; at: number };             // НОВЕ поле — суто адитивно
  at: number;
};

function toDTO(d: Device): DeviceDTO {
  return {
    id: d.id,
    temperature: d.temperature,                      // канон — єдина правда
    tempC: toCelsius(d.temperature),                 // старе виводимо з канону, щоб не розійшлись
    power: d.power && { watts: d.power.watts, at: d.power.at },
    at: d.lastReadingAt,
  };
}

// Стабільний конверт помилки: машинний код + людський текст, і НІЧОГО зсередини.
type ApiError = { error: { code: string; message: string } };

function toApiError(e: DomainError): ApiError {
  return { error: { code: e.code, message: e.publicMessage } };
  // ані stack, ані SQL, ані шляху файлу — нутрощі лишаються неопублікованими
}
