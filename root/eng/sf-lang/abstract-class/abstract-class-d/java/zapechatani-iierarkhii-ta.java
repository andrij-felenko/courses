// Java 17: запечатаний інтерфейс з фіксованим списком нащадків
public sealed interface Result<T> permits Success, Failure {}

public final class Success<T> implements Result<T> {
    private final T value;
    public Success(T value) { this.value = value; }
    public T value() { return value; }
}

public final class Failure<T> implements Result<T> {
    private final String error;
    public Failure(String error) { this.error = error; }
    public String error() { return error; }
}
