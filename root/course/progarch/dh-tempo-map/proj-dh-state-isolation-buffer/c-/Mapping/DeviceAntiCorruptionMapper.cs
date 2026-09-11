using System.Globalization;
using DigitalHomes.TempoBuffer.Models;

namespace DigitalHomes.TempoBuffer.Mapping;

/// <summary>
/// Транслятор антикорупційного шару (Anti-Corruption Layer, ACL).
/// Захищає доменне ядро від проникнення специфічних форматів вендорів,
/// невалідованих чисел і специфічних одиниць вимірювання.
/// </summary>
public class DeviceAntiCorruptionMapper
{
    /// <summary>
    /// Транслює сирий пакет телеметрії у чисту доменну сутність SensorReading.
    /// Повертає null, якщо пакет пошкоджено або значення виходить за фізичні межі.
    /// </summary>
    public SensorReading? MapToDomain(RawTelemetryPayload raw)
    {
        if (string.IsNullOrWhiteSpace(raw.DeviceUid) || string.IsNullOrWhiteSpace(raw.RawValue))
        {
            return null;
        }

        var timestamp = raw.TimestampEpochMs > 0
            ? DateTimeOffset.FromUnixTimeMilliseconds(raw.TimestampEpochMs).UtcDateTime
            : DateTime.UtcNow;

        // Нормалізація ідентифікатора пристрою (очищення від вендорних префіксів)
        var cleanDeviceId = raw.DeviceUid.Trim().ToLowerInvariant();

        // Парсинг та нормалізація показників залежно від типу пристрою
        if (raw.VendorType.Contains("temp", StringComparison.OrdinalIgnoreCase))
        {
            // Багато Zigbee-датчиків надсилають температуру, помножену на 100 (наприклад, 2350 = 23.5°C)
            if (!double.TryParse(raw.RawValue, NumberStyles.Any, CultureInfo.InvariantCulture, out var parsedValue))
            {
                return null;
            }

            var temperature = parsedValue > 500 ? parsedValue / 100.0 : parsedValue;

            // Фізична валідація інваріанта: допустимий діапазон температур для житлових приміщень
            if (temperature is < -40.0 or > 80.0)
            {
                return null; // Відкидаємо очевидний апаратний збій або шум АЦП
            }

            return new SensorReading(cleanDeviceId, SensorType.Temperature, Math.Round(temperature, 2), "°C", timestamp);
        }

        if (raw.VendorType.Contains("hum", StringComparison.OrdinalIgnoreCase))
        {
            if (!double.TryParse(raw.RawValue, NumberStyles.Any, CultureInfo.InvariantCulture, out var humidity))
            {
                return null;
            }

            var normalizedHum = humidity > 100 && humidity <= 10000 ? humidity / 100.0 : humidity;
            if (normalizedHum is < 0.0 or > 100.0)
            {
                return null;
            }

            return new SensorReading(cleanDeviceId, SensorType.Humidity, Math.Round(normalizedHum, 1), "%", timestamp);
        }

        if (raw.VendorType.Contains("motion", StringComparison.OrdinalIgnoreCase))
        {
            var isMotion = raw.RawValue.Equals("1", StringComparison.OrdinalIgnoreCase) ||
                           raw.RawValue.Equals("true", StringComparison.OrdinalIgnoreCase) ||
                           raw.RawValue.Equals("motion", StringComparison.OrdinalIgnoreCase);

            return new SensorReading(cleanDeviceId, SensorType.Motion, isMotion ? 1.0 : 0.0, "bool", timestamp);
        }

        // За замовчуванням повертаємо контактний датчик або невідомий тип як контакт
        var isContactOpen = raw.RawValue.Equals("open", StringComparison.OrdinalIgnoreCase) ||
                            raw.RawValue.Equals("1", StringComparison.OrdinalIgnoreCase);

        return new SensorReading(cleanDeviceId, SensorType.Contact, isContactOpen ? 1.0 : 0.0, "bool", timestamp);
    }
}
