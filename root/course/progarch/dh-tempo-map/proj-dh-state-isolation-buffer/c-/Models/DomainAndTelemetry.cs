namespace DigitalHomes.TempoBuffer.Models;

/// <summary>
/// Тип вимірювання датчика в доменній моделі.
/// </summary>
public enum SensorType
{
    Temperature,
    Humidity,
    Motion,
    Contact
}

/// <summary>
/// Тип дії для фізичного виконавчого пристрою (актуатора).
/// </summary>
public enum ActuatorAction
{
    TurnOn,
    TurnOff,
    SetLevel
}

/// <summary>
/// Сирий вхідний пакет телеметрії від зовнішнього пристрою чи шлюзу (Zigbee/MQTT/HTTP Webhook).
/// Містить вендорні назви полів, нетипізовані рядкові значення та апаратні мілівольти.
/// </summary>
public class RawTelemetryPayload
{
    public string DeviceUid { get; set; } = string.Empty;
    public string VendorType { get; set; } = string.Empty; // Наприклад: "tuya_temp_sensor_v2"
    public string RawValue { get; set; } = string.Empty;   // Наприклад: "2350" (23.50°C) або "true"
    public long TimestampEpochMs { get; set; }
    public int? BatteryMv { get; set; }                    // Наприклад: 2980 (мілівольти)
}

/// <summary>
/// Чиста доменна сутність показника датчика.
/// Забезпечує строгу типізацію, узгоджені одиниці вимірювання та валідовані діапазони.
/// </summary>
public record SensorReading(
    string DeviceId,
    SensorType Type,
    double Value,
    string Unit,
    DateTime TimestampUtc
);

/// <summary>
/// Чиста доменна команда керування актуатором (силовим реле, клапаном опалення).
/// </summary>
public record ActuatorCommand(
    string ActuatorId,
    ActuatorAction Action,
    double? Level,
    DateTime IssuedAtUtc
);
