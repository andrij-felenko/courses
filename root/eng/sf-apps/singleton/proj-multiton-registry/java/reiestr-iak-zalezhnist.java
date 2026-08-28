// БУЛО: прихована залежність від глобального реєстру логерів
class OrderService {
    void process(Order order) {
        Logger.get("orders").info("нове замовлення");  // ← незримий глобал
    }
}

// СТАЛО: реєстр — явна залежність конструктора
class OrderService {
    private final LoggerRegistry loggers;
    OrderService(LoggerRegistry loggers) { this.loggers = loggers; }  // ← видно в сигнатурі

    void process(Order order) {
        loggers.get("orders").info("нове замовлення");
    }
}

// збірка (композиційний корінь):
LoggerRegistry loggers = new LoggerRegistry();
OrderService orders = new OrderService(loggers);

// у тесті: свій реєстр на кожен тест, стан не тече між прогонами
OrderService sut = new OrderService(new FakeLoggerRegistry());
