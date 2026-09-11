using DigitalHomes.TempoBuffer.Buffering;
using DigitalHomes.TempoBuffer.Models;

namespace DigitalHomes.TempoBuffer;

/// <summary>
/// Демонстраційний стенд роботи StateIsolationBuffer.
/// Імітує сплеск високочастотної телеметрії сенсорів та коливання команд термостата,
/// демонструючи захист доменного ядра та фізичного реле.
/// </summary>
public class Program
{
    public static async Task Main(string[] args)
    {
        Console.OutputEncoding = System.Text.Encoding.UTF8;
        Console.WriteLine("=== Digital Homes: Стенд буфера ізоляції стану (StateIsolationBuffer) ===\n");

        var dispatchedToHardware = new List<ActuatorCommand>();

        // Створюємо буфер із вікном дедуплікації 300 мс та інтервалом захисту реле 500 мс
        await using var buffer = new StateIsolationBuffer(
            deduplicationWindow: TimeSpan.FromMilliseconds(300),
            actuatorCooldown: TimeSpan.FromMilliseconds(500),
            hardwareDispatcher: cmd =>
            {
                lock (dispatchedToHardware)
                {
                    dispatchedToHardware.Add(cmd);
                    Console.WriteLine($"  [ФІЗИЧНЕ ЗАЛІЗО] Реле {cmd.ActuatorId} перемкнуто в стан: {cmd.Action} о {cmd.IssuedAtUtc:HH:mm:ss.fff}");
                }
            }
        );

        // -------------------------------------------------------------------------
        // СЦЕНАРІЙ 1: Шторм вхідних вебхуків від зашумленого сенсора температури
        // -------------------------------------------------------------------------
        Console.WriteLine("1. Симуляція сплеску телеметрії: 50 вебхуків за 100 мс із повторами...");

        var nowMs = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds();
        for (var i = 0; i < 50; i++)
        {
            // Більшість пакетів дублюють одне й те саме значення 21.4°C із мікрошумом
            var rawTemp = i % 10 == 0 ? "2250" : "2140";
            var raw = new RawTelemetryPayload
            {
                DeviceUid = "zigbee-temp-livingroom",
                VendorType = "tuya_temp_sensor_v2",
                RawValue = rawTemp,
                TimestampEpochMs = nowMs + i,
                BatteryMv = 3000
            };

            buffer.IngestRawTelemetry(raw);
        }

        Console.WriteLine($"   Вхідних пакетів: {buffer.IngestedCount}");
        Console.WriteLine($"   Відсіяно дедуплікатором: {buffer.DroppedDuplicatesCount}");
        Console.WriteLine($"   Пропущено в доменний кеш: {buffer.PromotedToDomainCount}");

        var snapshot = buffer.GetCurrentState("zigbee-temp-livingroom", SensorType.Temperature);
        Console.WriteLine($"   Актуальний стан у кеші: {snapshot?.Value} {snapshot?.Unit}\n");

        // -------------------------------------------------------------------------
        // СЦЕНАРІЙ 2: Високочастотні коливання команд термостата (захист реле)
        // -------------------------------------------------------------------------
        Console.WriteLine("2. Симуляція швидких коливань термостата (увімк/вимк кожні 50 мс)...");

        for (var i = 0; i < 10; i++)
        {
            var action = (i % 2 == 0) ? ActuatorAction.TurnOn : ActuatorAction.TurnOff;
            var command = new ActuatorCommand("boiler-relay-01", action, null, DateTime.UtcNow);
            await buffer.SendActuatorCommandAsync(command);
            await Task.Delay(50); // Команди генеруються набагато швидше, ніж дозволяє фізичний кулдаун реле
        }

        // Даємо час фоновому обробнику завершити чергу
        await Task.Delay(600);

        Console.WriteLine($"\n   Команд надіслано ядром: 10");
        Console.WriteLine($"   Передано на фізичне реле: {buffer.DispatchedCommandsCount}");
        Console.WriteLine($"   Загашено тротлінгом для захисту контактів: {buffer.SuppressedCommandsCount}");

        Console.WriteLine("\n=== Висновок: Буфер темпів успішно захистив ядро від лавини подій та вберіг реле від зносу. ===");
    }
}
