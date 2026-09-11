namespace DigitalHomes.Entities;

/// <summary>
/// Доменна сутність кімнати в системі розумного будинку.
/// Зберігає параметри клімату та колекцію підключених датчиків і пристроїв.
/// </summary>
public class RoomEntity
{
    public int Id { get; set; }
    public string Name { get; set; } = string.Empty;
    public double TargetTemperature { get; set; }
    public double TargetHumidity { get; set; }

    // Модифікатор virtual необхідний для генерації динамічного проксі-класу
    // бібліотекою EF Core, який перехоплює звернення до властивості та підвантажує дані (Lazy Loading).
    public virtual ICollection<DeviceEntity> Devices { get; set; } = new List<DeviceEntity>();
}

/// <summary>
/// Доменна сутність виконавчого пристрою або сенсора, прив'язаного до кімнати.
/// </summary>
public class DeviceEntity
{
    public int Id { get; set; }
    public int RoomId { get; set; }
    public string Type { get; set; } = string.Empty; // Наприклад: "Thermostat", "Humidifier", "AirQualitySensor"
    public string SerialNumber { get; set; } = string.Empty;
    public bool IsActive { get; set; }

    // Навігаційна властивість зворотного зв'язку з батьківською сутністю.
    public virtual RoomEntity? Room { get; set; }
}
