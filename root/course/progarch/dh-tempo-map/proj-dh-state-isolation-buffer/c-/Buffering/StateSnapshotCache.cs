using System.Collections.Concurrent;
using DigitalHomes.TempoBuffer.Models;

namespace DigitalHomes.TempoBuffer.Buffering;

/// <summary>
/// Потокобезпечний кеш останніх відомих знімків стану сенсорів у пам'яті.
/// Розв'язує задачу асинхронного читання: веб-клієнти та фонові аналізатори миттєво
/// отримують актуальний стан без звернення до бази даних і без опитування заліза.
/// </summary>
public class StateSnapshotCache
{
    private readonly ConcurrentDictionary<string, SensorReading> _snapshots = new();

    /// <summary>
    /// Атомарно оновлює останній стан датчика, якщо нове показання є свіжішим за часом.
    /// </summary>
    public void Update(SensorReading reading)
    {
        var key = $"{reading.DeviceId}:{reading.Type}";

        _snapshots.AddOrUpdate(
            key,
            reading,
            (_, existing) => reading.TimestampUtc >= existing.TimestampUtc ? reading : existing
        );
    }

    /// <summary>
    /// Повертає актуальний знімок стану конкретного датчика.
    /// </summary>
    public bool TryGet(string deviceId, SensorType type, out SensorReading? reading)
    {
        var key = $"{deviceId}:{type}";
        return _snapshots.TryGetValue(key, out reading);
    }

    /// <summary>
    /// Повертає знімки всіх зареєстрованих датчиків у системі.
    /// </summary>
    public IReadOnlyCollection<SensorReading> GetAll() => _snapshots.Values.ToList();

    public int Count => _snapshots.Count;
}
