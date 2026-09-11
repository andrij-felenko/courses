using System;
using System.Collections.Generic;
using System.Linq;
using DigitalHomes.ClimateControl.Domain;
using DigitalHomes.ClimateControl.Infrastructure;

namespace DigitalHomes.ClimateControl.Application;

/// <summary>
/// Антипатерн Pass-Through Layer (транзитний шар).
/// Сервіс застосунку, який штучно проганяє запити аналітичного читання
/// крізь репозиторій та важкі доменні агрегати з подальшим мапінгом у DTO.
/// </summary>
public sealed class PassThroughClimateService
{
    private readonly IRoomRepository _roomRepository;

    public PassThroughClimateService(IRoomRepository roomRepository)
    {
        _roomRepository = roomRepository;
    }

    /// <summary>
    /// Командний шлях (Command): доменний агрегат тут дійсно потрібен,
    /// оскільки він гарантує дотримання бізнес-інваріантів та гістерезису.
    /// </summary>
    public void Handle(SetTemperatureCommand command)
    {
        Room room = _roomRepository.GetById(command.RoomId)
            ?? throw new KeyNotFoundException($"Кімнату з ID {command.RoomId} не знайдено.");

        Temperature target = Temperature.FromCelsius(command.TargetTemperatureCelsius);
        room.SetTargetTemperature(target);

        _roomRepository.Save(room);
    }

    /// <summary>
    /// Антипатерн читання: запит на отримання дашборду завантажує повні
    /// доменні сутності з бази, інстанціює сотні агрегатів Room та об'єктів-значень
    /// Temperature, після чого одразу ж викидає їх на користь пласких DTO.
    /// Це створює паразитарне навантаження на купу пам'яті та прибиральник сміття (GC churn).
    /// </summary>
    public ClimateDashboardDto GetClimateDashboard()
    {
        // 1. Репозиторій підіймає важкі доменні об'єкти
        IReadOnlyList<Room> rooms = _roomRepository.GetAllRooms();

        // 2. Бюрократичний ручний мапінг сутностей у DTO
        var dtos = new List<RoomClimateDto>(rooms.Count);
        double sumCurrent = 0;
        double sumTarget = 0;
        int activeHeating = 0;

        foreach (Room room in rooms)
        {
            dtos.Add(new RoomClimateDto
            {
                RoomId = room.Id,
                RoomName = room.Name,
                CurrentTemp = room.CurrentTemperature.Value,
                TargetTemp = room.TargetTemperature.Value,
                Mode = room.Mode.ToString(),
                IsHeatingActive = room.IsHeatingActive
            });

            sumCurrent += room.CurrentTemperature.Value;
            sumTarget += room.TargetTemperature.Value;
            if (room.IsHeatingActive)
            {
                activeHeating++;
            }
        }

        double avgCurrent = rooms.Count > 0 ? Math.Round(sumCurrent / rooms.Count, 1) : 0;
        double avgTarget = rooms.Count > 0 ? Math.Round(sumTarget / rooms.Count, 1) : 0;

        return new ClimateDashboardDto(dtos, avgCurrent, avgTarget, activeHeating, DateTime.UtcNow);
    }
}
