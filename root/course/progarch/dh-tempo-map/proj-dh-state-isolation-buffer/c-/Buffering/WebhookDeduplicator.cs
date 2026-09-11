using System.Collections.Concurrent;
using DigitalHomes.TempoBuffer.Models;

namespace DigitalHomes.TempoBuffer.Buffering;

/// <summary>
/// Конвеєр дедуплікації та згладжування високочастотних вхідних подій.
/// Гасить пікові шторми вебхуків: якщо сенсор надсилає сотні ідентичних або незначно
/// відмінних повідомлень за секунду, дедуплікатор пропускає лише суттєві зміни
/// або події після закінчення часового вікна охолодження.
/// </summary>
public class WebhookDeduplicator
{
    private readonly TimeSpan _window;
    private readonly double _temperatureEpsilon;
    private readonly ConcurrentDictionary<string, (double LastValue, DateTime LastProcessedUtc)> _history = new();

    public WebhookDeduplicator(TimeSpan? window = null, double temperatureEpsilon = 0.1)
    {
        _window = window ?? TimeSpan.FromMilliseconds(500);
        _temperatureEpsilon = temperatureEpsilon;
    }

    /// <summary>
    /// Перевіряє, чи варто передавати показання далі в доменний контур.
    /// Відсікає дублікати та мікрошум датчиків (jitter).
    /// </summary>
    public bool ShouldProcess(SensorReading reading)
    {
        var key = $"{reading.DeviceId}:{reading.Type}";
        var now = DateTime.UtcNow;

        return _history.AddOrUpdate(
            key,
            _ => (reading.Value, now),
            (_, old) =>
            {
                var timeElapsed = now - old.LastProcessedUtc;
                var valueDiff = Math.Abs(reading.Value - old.LastValue);

                // Для температурних сенсорів дрібні коливання (наприклад, 0.02°C) є шумом АЦП
                var isSignificantChange = reading.Type switch
                {
                    SensorType.Temperature => valueDiff >= _temperatureEpsilon,
                    SensorType.Humidity => valueDiff >= 0.5,
                    _ => valueDiff > 0.001
                };

                // Пропускаємо, якщо змінилося значення або минуло вікно обов'язкового heartbeat
                if (isSignificantChange || timeElapsed >= _window)
                {
                    return (reading.Value, now);
                }

                // Інакше зберігаємо попереднє зареєстроване значення (подія гаситься)
                return old;
            }
        ).LastProcessedUtc == now;
    }

    public void Clear() => _history.Clear();
}
