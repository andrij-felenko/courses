using System;
using System.Collections.Generic;
using System.Data;
using Dapper;
using DigitalHomes.ClimateControl.Domain;
using Microsoft.Data.Sqlite;

namespace DigitalHomes.ClimateControl.Infrastructure;

/// <summary>
/// Інтерфейс репозиторію для транзакційного шляху запису команд.
/// </summary>
public interface IRoomRepository
{
    Room? GetById(Guid id);
    IReadOnlyList<Room> GetAllRooms();
    void Save(Room room);
}

/// <summary>
/// Реалізація репозиторію на базі SQLite.
/// Відновлює повні доменні агрегати Room із перевіркою коректності стану.
/// </summary>
public sealed class RoomRepository : IRoomRepository
{
    private readonly IDbConnection _connection;

    public RoomRepository(IDbConnection connection)
    {
        _connection = connection;
    }

    public Room? GetById(Guid id)
    {
        const string sql = """
            SELECT Id, Name, CurrentTemperature, TargetTemperature, Mode, IsHeatingActive, LastUpdatedUtc
            FROM Rooms
            WHERE Id = @Id;
            """;

        RoomRecord? row = _connection.QuerySingleOrDefault<RoomRecord>(sql, new { Id = id.ToString() });
        return row is null ? null : MapToDomain(row);
    }

    public IReadOnlyList<Room> GetAllRooms()
    {
        const string sql = """
            SELECT Id, Name, CurrentTemperature, TargetTemperature, Mode, IsHeatingActive, LastUpdatedUtc
            FROM Rooms;
            """;

        IEnumerable<RoomRecord> rows = _connection.Query<RoomRecord>(sql);
        var list = new List<Room>();

        foreach (RoomRecord row in rows)
        {
            list.Add(MapToDomain(row));
        }

        return list;
    }

    public void Save(Room room)
    {
        const string sql = """
            UPDATE Rooms
            SET 
                TargetTemperature = @TargetTemperature,
                CurrentTemperature = @CurrentTemperature,
                Mode = @Mode,
                IsHeatingActive = @IsHeatingActive,
                LastUpdatedUtc = @LastUpdatedUtc
            WHERE Id = @Id;
            """;

        _connection.Execute(sql, new
        {
            Id = room.Id.ToString(),
            TargetTemperature = room.TargetTemperature.Value,
            CurrentTemperature = room.CurrentTemperature.Value,
            Mode = room.Mode.ToString(),
            IsHeatingActive = room.IsHeatingActive ? 1 : 0,
            LastUpdatedUtc = room.LastUpdatedUtc.ToString("o")
        });
    }

    private static Room MapToDomain(RoomRecord r)
    {
        return new Room(
            Guid.Parse(r.Id),
            r.Name,
            Temperature.FromCelsius(r.CurrentTemperature),
            Temperature.FromCelsius(r.TargetTemperature),
            Enum.Parse<HvacMode>(r.Mode),
            r.IsHeatingActive == 1,
            DateTime.Parse(r.LastUpdatedUtc));
    }

    private sealed class RoomRecord
    {
        public string Id { get; set; } = string.Empty;
        public string Name { get; set; } = string.Empty;
        public double CurrentTemperature { get; set; }
        public double TargetTemperature { get; set; }
        public string Mode { get; set; } = string.Empty;
        public int IsHeatingActive { get; set; }
        public string LastUpdatedUtc { get; set; } = string.Empty;
    }
}

/// <summary>
/// Ініціалізатор бази даних SQLite in-memory з тестовими даними.
/// </summary>
public static class ClimateDatabase
{
    public static SqliteConnection CreateAndSeed(int roomCount = 50)
    {
        // In-memory з'єднання залишається відкритим протягом усього життя застосунку
        var connection = new SqliteConnection("Data Source=:memory:;Mode=Memory;Cache=Shared");
        connection.Open();

        const string createTableSql = """
            CREATE TABLE IF NOT EXISTS Rooms (
                Id TEXT PRIMARY KEY,
                Name TEXT NOT NULL,
                CurrentTemperature REAL NOT NULL,
                TargetTemperature REAL NOT NULL,
                Mode TEXT NOT NULL,
                IsHeatingActive INTEGER NOT NULL,
                LastUpdatedUtc TEXT NOT NULL
            );
            """;

        connection.Execute(createTableSql);

        var random = new Random(42);
        string[] roomTypes = ["Вітальня", "Спальня", "Кухня", "Кабінет", "Дитяча", "Ванна", "Коридор", "Мансарда"];

        var seedList = new List<object>(roomCount);
        for (int i = 1; i <= roomCount; i++)
        {
            string type = roomTypes[(i - 1) % roomTypes.Length];
            double current = Math.Round(18.0 + random.NextDouble() * 5.0, 1);
            double target = Math.Round(20.0 + random.NextDouble() * 4.0, 1);
            bool isHeating = current < target - 0.3;

            seedList.Add(new
            {
                Id = Guid.NewGuid().ToString(),
                Name = $"{type} #{i}",
                CurrentTemperature = current,
                TargetTemperature = target,
                Mode = HvacMode.Comfort.ToString(),
                IsHeatingActive = isHeating ? 1 : 0,
                LastUpdatedUtc = DateTime.UtcNow.ToString("o")
            });
        }

        const string insertSql = """
            INSERT INTO Rooms (Id, Name, CurrentTemperature, TargetTemperature, Mode, IsHeatingActive, LastUpdatedUtc)
            VALUES (@Id, @Name, @CurrentTemperature, @TargetTemperature, @Mode, @IsHeatingActive, @LastUpdatedUtc);
            """;

        connection.Execute(insertSql, seedList);
        return connection;
    }
}
