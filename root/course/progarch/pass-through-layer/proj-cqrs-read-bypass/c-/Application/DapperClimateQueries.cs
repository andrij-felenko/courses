using System;
using System.Collections.Generic;
using System.Data;
using System.Linq;
using Dapper;

namespace DigitalHomes.ClimateControl.Application;

/// <summary>
/// Оптимізований канал обходу (Bypass Channel за патерном CQRS).
/// Робить пряму SQL-проєкцію з бази даних одразу в цільові DTO без залучення
/// репозиторію, доменних агрегатів Room, об'єктів-значень та проміжних маперів.
/// </summary>
public sealed class DapperClimateQueries
{
    private readonly IDbConnection _connection;

    public DapperClimateQueries(IDbConnection connection)
    {
        _connection = connection;
    }

    /// <summary>
    /// Швидке читання зведеного дашборду:
    /// Виконує один легкий SQL-запит і дозволяє Dapper безпосередньо матеріалізувати
    /// пласкі поля в RoomClimateDto. Мінімізує алокації та час виконання.
    /// </summary>
    public ClimateDashboardDto GetClimateDashboard()
    {
        const string sql = """
            SELECT 
                Id AS RoomId,
                Name AS RoomName,
                CurrentTemperature AS CurrentTemp,
                TargetTemperature AS TargetTemp,
                Mode,
                IsHeatingActive
            FROM Rooms;
            """;

        // Пряма матеріалізація в DTO в один прохід
        List<RoomClimateDto> rooms = _connection.Query<RoomClimateDto>(sql).AsList();

        double sumCurrent = 0;
        double sumTarget = 0;
        int activeHeating = 0;

        for (int i = 0; i < rooms.Count; i++)
        {
            RoomClimateDto room = rooms[i];
            sumCurrent += room.CurrentTemp;
            sumTarget += room.TargetTemp;
            if (room.IsHeatingActive)
            {
                activeHeating++;
            }
        }

        double avgCurrent = rooms.Count > 0 ? Math.Round(sumCurrent / rooms.Count, 1) : 0;
        double avgTarget = rooms.Count > 0 ? Math.Round(sumTarget / rooms.Count, 1) : 0;

        return new ClimateDashboardDto(rooms, avgCurrent, avgTarget, activeHeating, DateTime.UtcNow);
    }
}
