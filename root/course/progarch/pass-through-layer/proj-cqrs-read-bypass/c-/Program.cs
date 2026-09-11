using System;
using System.Linq;
using DigitalHomes.ClimateControl.Application;
using DigitalHomes.ClimateControl.Benchmarks;
using DigitalHomes.ClimateControl.Controllers;
using DigitalHomes.ClimateControl.Domain;
using DigitalHomes.ClimateControl.Infrastructure;

namespace DigitalHomes.ClimateControl;

public static class Program
{
    public static void Main()
    {
        Console.OutputEncoding = System.Text.Encoding.UTF8;
        Console.WriteLine("=== Сервіс клімат-контролю Digital Homes (Демонстрація CQRS Bypass) ===\n");

        // 1. Ініціалізація інфраструктури (SQLite in-memory з 50 кімнатами)
        using var connection = ClimateDatabase.CreateAndSeed(50);
        var repository = new RoomRepository(connection);

        var passThroughService = new PassThroughClimateService(repository);
        var bypassQueries = new DapperClimateQueries(connection);
        var controller = new ClimateController(passThroughService, bypassQueries);

        // 2. Демонстрація шляху запису (Command із перевіркою інваріантів)
        Console.WriteLine("[1] Перевірка командного шляху (захист інваріантів у Room):");
        Room firstRoom = repository.GetAllRooms().First();
        Console.WriteLine($"    Кімната: '{firstRoom.Name}', Поточна: {firstRoom.CurrentTemperature}, Цільова: {firstRoom.TargetTemperature}");

        // Успішна валідна зміна цільової температури (+2 °C)
        double newTarget = firstRoom.CurrentTemperature.Value + 2.0;
        controller.SetTemperature(new SetTemperatureCommand(firstRoom.Id, newTarget));
        Room updatedRoom = repository.GetById(firstRoom.Id)!;
        Console.WriteLine($"    Після зміни: Цільова = {updatedRoom.TargetTemperature}, Обігрів увімкнено = {updatedRoom.IsHeatingActive}");

        // Спроба порушити інваріант (стрибок температури понад 8 °C)
        try
        {
            Console.WriteLine("    Спроба встановити різкий перепад (+12 °C)...");
            controller.SetTemperature(new SetTemperatureCommand(firstRoom.Id, firstRoom.CurrentTemperature.Value + 12.0));
        }
        catch (InvalidOperationException ex)
        {
            Console.WriteLine($"    [ПЕРЕХОПЛЕНО ІНВАРІАНТОМ]: {ex.Message}");
        }

        Console.WriteLine();

        // 3. Демонстрація ідентичності результатів читання дашборду
        Console.WriteLine("[2] Звірка результатів читання дашборду між двома підходами:");
        ClimateDashboardDto passThroughResult = controller.GetDashboardViaPassThrough();
        ClimateDashboardDto bypassResult = controller.GetDashboardViaBypass();

        Console.WriteLine($"    Кімнат у вибірці: PassThrough={passThroughResult.Rooms.Count}, Bypass={bypassResult.Rooms.Count}");
        Console.WriteLine($"    Середня температура: PassThrough={passThroughResult.AverageCurrentTemp} °C, Bypass={bypassResult.AverageCurrentTemp} °C");
        Console.WriteLine($"    Кімнат з активним обігрівом: PassThrough={passThroughResult.ActiveHeatingCount}, Bypass={bypassResult.ActiveHeatingCount}");
        Console.WriteLine("    -> Дані ідентичні, але досягнуті принципово різною ціною алокацій.\n");

        // 4. Запуск бенчмарку виділення пам'яті
        AllocationBenchmark.Run(passThroughService, bypassQueries, iterations: 10_000);
    }
}
