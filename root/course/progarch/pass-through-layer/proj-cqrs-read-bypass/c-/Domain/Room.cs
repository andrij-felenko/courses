using System;

namespace DigitalHomes.ClimateControl.Domain;

/// <summary>
/// Режим роботи кліматичної системи кімнати.
/// </summary>
public enum HvacMode
{
    Off,
    Eco,
    Comfort,
    Boost
}

/// <summary>
/// Доменний агрегат кімнати (Aggregate Root).
/// Захищає транзакційні бізнес-інваріанти під час зміни температури та перемикання режимів.
/// </summary>
public sealed class Room
{
    public const double MaxSingleStepDelta = 8.0;

    public Guid Id { get; }
    public string Name { get; }
    public Temperature CurrentTemperature { get; private set; }
    public Temperature TargetTemperature { get; private set; }
    public HvacMode Mode { get; private set; }
    public bool IsHeatingActive { get; private set; }
    public DateTime LastUpdatedUtc { get; private set; }

    public Room(
        Guid id,
        string name,
        Temperature currentTemperature,
        Temperature targetTemperature,
        HvacMode mode,
        bool isHeatingActive,
        DateTime lastUpdatedUtc)
    {
        if (string.IsNullOrWhiteSpace(name))
            throw new ArgumentException("Назва кімнати не може бути порожньою.", nameof(name));

        Id = id;
        Name = name;
        CurrentTemperature = currentTemperature;
        TargetTemperature = targetTemperature;
        Mode = mode;
        IsHeatingActive = isHeatingActive;
        LastUpdatedUtc = lastUpdatedUtc;
    }

    /// <summary>
    /// Встановлює нову цільову температуру із захистом доменних інваріантів.
    /// Запобігає тепловому удару та надмірному навантаженню на нагрівальний котел.
    /// </summary>
    public void SetTargetTemperature(Temperature newTarget)
    {
        if (Mode == HvacMode.Off)
        {
            throw new InvalidOperationException(
                $"Неможливо змінити температуру для кімнати '{Name}', оскільки клімат-контроль вимкнено.");
        }

        double delta = Math.Abs(newTarget.Value - CurrentTemperature.Value);
        if (delta > MaxSingleStepDelta)
        {
            throw new InvalidOperationException(
                $"Заборонено одноразову зміну температури на {delta:F1} °C. Максимальний допустимий крок — {MaxSingleStepDelta} °C.");
        }

        TargetTemperature = newTarget;
        RecalculateHeatingState();
        LastUpdatedUtc = DateTime.UtcNow;
    }

    /// <summary>
    /// Оновлює показники з фізичного датчика температури в кімнаті.
    /// </summary>
    public void RecordSensorReading(Temperature measuredTemperature)
    {
        CurrentTemperature = measuredTemperature;
        RecalculateHeatingState();
        LastUpdatedUtc = DateTime.UtcNow;
    }

    /// <summary>
    /// Змінює режим роботи термостата.
    /// </summary>
    public void ChangeMode(HvacMode newMode)
    {
        Mode = newMode;
        RecalculateHeatingState();
        LastUpdatedUtc = DateTime.UtcNow;
    }

    private void RecalculateHeatingState()
    {
        if (Mode == HvacMode.Off)
        {
            IsHeatingActive = false;
            return;
        }

        // Гістерезис 0.3 °C для запобігання постійному перемиканню реле
        IsHeatingActive = CurrentTemperature.Value < (TargetTemperature.Value - 0.3);
    }
}
