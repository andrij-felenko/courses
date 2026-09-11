using System;

namespace DigitalHomes.ClimateControl.Domain;

/// <summary>
/// Об'єкт-значення (Value Object) температури в градусах Цельсія.
/// Гарантує фізичну коректність та валідність діапазону для житлових приміщень.
/// </summary>
public readonly record struct Temperature : IComparable<Temperature>
{
    public const double MinCelsius = 5.0;
    public const double MaxCelsius = 35.0;

    public double Value { get; }

    private Temperature(double value)
    {
        Value = Math.Round(value, 1, MidpointRounding.AwayFromZero);
    }

    public static Temperature FromCelsius(double value)
    {
        if (value < MinCelsius || value > MaxCelsius)
        {
            throw new ArgumentOutOfRangeException(
                nameof(value),
                value,
                $"Температура має бути в межах від {MinCelsius} °C до {MaxCelsius} °C.");
        }

        return new Temperature(value);
    }

    public int CompareTo(Temperature other) => Value.CompareTo(other.Value);

    public static bool operator <(Temperature left, Temperature right) => left.Value < right.Value;
    public static bool operator >(Temperature left, Temperature right) => left.Value > right.Value;
    public static bool operator <=(Temperature left, Temperature right) => left.Value <= right.Value;
    public static bool operator >=(Temperature left, Temperature right) => left.Value >= right.Value;

    public override string ToString() => $"{Value:F1} °C";
}
