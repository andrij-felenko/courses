int main() {
    // 1. Створення статичного конвеєра валідації
    constexpr EventPipeline pipeline{
        TimestampFilter{ .min_allowed_time = 1000 },
        PowerFilter{ .max_voltage = 24.5, .max_current = 10.0 },
        CommandPriorityFilter{ .min_priority = 1 }
    };

    // 2. Створення ланцюжка протоколювання подій
    const ActionPipeline logging_pipeline{
        [](const auto& ev) { std::cout << "-> [ЛОГ СИСТЕМИ] Час події: " << ev.timestamp << '\n'; },
        [](const auto&)    { std::cout << "-> [МЕТРИКИ] Лічильник оброблених пакетів +1\n"; }
    };

    // 3. Створення диспетчера кінцевих дій
    const EventDispatcher dispatcher;

    // 4. Набір вхідних тестових подій
    const EventVariant events[] = {
        // Валідна телеметрія
        TelemetryEvent{ .timestamp = 1050, .voltage = 12.4, .current = 2.1, .temperature = 38.5 },
        // Невалідна телеметрія: перевищення максимальної напруги 24.5 В
        TelemetryEvent{ .timestamp = 1100, .voltage = 28.2, .current = 1.5, .temperature = 41.0 },
        // Невалідна команда: пріоритет 0 нижчий за поріг фільтра
        CommandEvent{ .timestamp = 1200, .command = "SYSTEM_SHUTDOWN", .priority = 0 },
        // Валідна команда
        CommandEvent{ .timestamp = 1300, .command = "CALIBRATE_GYRO", .priority = 5 }
    };

    for (const auto& ev : events) {
        std::cout << "\n--- Обробка нового повідомлення ---\n";
        
        const bool is_valid = std::visit([&](const auto& concrete_event) {
            return pipeline.process(concrete_event);
        }, ev);

        if (is_valid) {
            std::visit([&](const auto& concrete_event) {
                logging_pipeline.execute(concrete_event);
            }, ev);
            dispatcher.dispatch(ev);
        } else {
            std::cout << "[ВІДХИЛЕНО] Подія не пройшла перевірку фільтрами конвеєра!\n";
        }
    }

    return 0;
}
