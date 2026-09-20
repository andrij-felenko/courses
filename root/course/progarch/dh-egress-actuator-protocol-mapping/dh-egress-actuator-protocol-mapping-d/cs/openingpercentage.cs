// Захист бізнес-інваріанта: фабричний метод відсікає некоректні значення до створення об'єкта
public readonly record struct OpeningPercentage
{
    public double Value { get; }

    private OpeningPercentage(double value) => Value = value;

    public static Result<OpeningPercentage, DomainError> Create(double rawValue)
    {
        if (double.IsNaN(rawValue) || rawValue is < 0.0 or > 100.0)
        {
            return Result.Failure<OpeningPercentage, DomainError>(
                new DomainError("Відсоток відкриття має лежати в межах від 0.0 до 100.0%.")
            );
        }

        return Result.Success<OpeningPercentage, DomainError>(new OpeningPercentage(rawValue));
    }
}
