namespace DigitalHomes.Contracts;

/// <summary>
/// Незмінний контракт даних пристрою для передачі через API.
/// Повністю відв'язаний від атрибутів і трекінгу Entity Framework.
/// </summary>
public record DeviceDto(
    int Id,
    string Type,
    string SerialNumber,
    bool IsActive
);

/// <summary>
/// Незмінний контракт відповіді з даними кімнати.
/// Містить рівно ті поля, які очікує споживач інтерфейсу, і жодних навігаційних посилань ORM.
/// </summary>
public record RoomResponseDto(
    int Id,
    string Name,
    double TargetTemperature,
    double TargetHumidity,
    IReadOnlyList<DeviceDto> Devices
);

/// <summary>
/// Контракт команди зміни цільових кліматичних показників кімнати.
/// Захищає від вразливості масового призначення (Over-posting), приймаючи лише дозволені параметри.
/// </summary>
public record UpdateRoomClimateCommand(
    double TargetTemperature,
    double TargetHumidity
);
