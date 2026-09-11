using System;
using System.Collections.Generic;

namespace DigitalHomes.ClimateControl.Application;

/// <summary>
/// Команда на зміну цільової температури кімнати (Шлях запису / Command).
/// </summary>
public sealed record SetTemperatureCommand(Guid RoomId, double TargetTemperatureCelsius);

/// <summary>
/// Пласка DTO-модель стану клімату окремої кімнати (Шлях читання / Query).
/// </summary>
public sealed class RoomClimateDto
{
    public Guid RoomId { get; set; }
    public string RoomName { get; set; } = string.Empty;
    public double CurrentTemp { get; set; }
    public double TargetTemp { get; set; }
    public string Mode { get; set; } = string.Empty;
    public bool IsHeatingActive { get; set; }
}

/// <summary>
/// Зведена аналітична панель моніторингу клімату будинку (Дашборд).
/// </summary>
public sealed record ClimateDashboardDto(
    IReadOnlyList<RoomClimateDto> Rooms,
    double AverageCurrentTemp,
    double AverageTargetTemp,
    int ActiveHeatingCount,
    DateTime GeneratedAtUtc);
