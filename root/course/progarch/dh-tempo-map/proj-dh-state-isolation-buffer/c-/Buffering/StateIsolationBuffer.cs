using DigitalHomes.TempoBuffer.Mapping;
using DigitalHomes.TempoBuffer.Models;

namespace DigitalHomes.TempoBuffer.Buffering;

/// <summary>
/// Центральний координатор буфера ізоляції стану (StateIsolationBuffer).
/// Виступає амортизатором між трьома годинниками системи Digital Homes:
/// 1. Швидкий контур (мілісекунди) — вхідні вебхуки сенсорів (дедуплікація та ACL).
/// 2. Середній контур (секунди) — доменне ядро та кеш останніх знімків стану.
/// 3. Повільний контур (хвилини) — тротлінг-черга команд для фізичних реле.
/// </summary>
public class StateIsolationBuffer : IAsyncDisposable
{
    private readonly DeviceAntiCorruptionMapper _mapper;
    private readonly WebhookDeduplicator _deduplicator;
    private readonly StateSnapshotCache _cache;
    private readonly ThrottledActuatorQueue _actuatorQueue;

    public int IngestedCount { get; private set; }
    public int DroppedDuplicatesCount { get; private set; }
    public int PromotedToDomainCount { get; private set; }

    public StateIsolationBuffer(
        TimeSpan? deduplicationWindow = null,
        TimeSpan? actuatorCooldown = null,
        Action<ActuatorCommand>? hardwareDispatcher = null)
    {
        _mapper = new DeviceAntiCorruptionMapper();
        _deduplicator = new WebhookDeduplicator(deduplicationWindow);
        _cache = new StateSnapshotCache();
        _actuatorQueue = new ThrottledActuatorQueue(actuatorCooldown, hardwareDispatcher);
    }

    /// <summary>
    /// Вхідна точка для прийому сирої телеметрії.
    /// Повертає true, якщо подія пройшла крізь ACL та дедуплікатор і оновила кеш стану.
    /// </summary>
    public bool IngestRawTelemetry(RawTelemetryPayload rawPayload)
    {
        IngestedCount++;

        // 1. Антикорупційний мапер ізолює вендорну схему
        var reading = _mapper.MapToDomain(rawPayload);
        if (reading == null)
        {
            return false;
        }

        // 2. Дедуплікатор гасить високочастотні повтори та шум
        if (!_deduplicator.ShouldProcess(reading))
        {
            DroppedDuplicatesCount++;
            return false;
        }

        // 3. Кеш оновлює останній валідний знімок для швидкого читання
        _cache.Update(reading);
        PromotedToDomainCount++;
        return true;
    }

    /// <summary>
    /// Миттєвий доступ до актуального стану пристрою без навантаження на мережу.
    /// </summary>
    public SensorReading? GetCurrentState(string deviceId, SensorType type)
    {
        _cache.TryGet(deviceId, type, out var reading);
        return reading;
    }

    /// <summary>
    /// Відправляє команду актуатору крізь тротлінг-чергу для захисту фізичного заліза.
    /// </summary>
    public ValueTask SendActuatorCommandAsync(ActuatorCommand command)
    {
        return _actuatorQueue.EnqueueAsync(command);
    }

    public int DispatchedCommandsCount => _actuatorQueue.DispatchedCount;
    public int SuppressedCommandsCount => _actuatorQueue.SuppressedCount;

    public async ValueTask DisposeAsync()
    {
        await _actuatorQueue.DisposeAsync();
    }
}
