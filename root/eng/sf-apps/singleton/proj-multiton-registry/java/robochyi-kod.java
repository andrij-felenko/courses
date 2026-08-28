// Java: computeIfAbsent на ConcurrentHashMap — АТОМАРНИЙ get-or-create.
// Перевірка й вставка — під внутрішнім замком сегмента мапи, одним кроком.
public final class LoggerRegistry {
    private final ConcurrentMap<String, Logger> loggers = new ConcurrentHashMap<>();

    public Logger get(String name) {
        // якщо ключа нема — викликає Logger::new РІВНО раз, навіть під десятком потоків;
        // решта чекають і отримують той самий створений екземпляр
        return loggers.computeIfAbsent(name, Logger::new);
    }
}
