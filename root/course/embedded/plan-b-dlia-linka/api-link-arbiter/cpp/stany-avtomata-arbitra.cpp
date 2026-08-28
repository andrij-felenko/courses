namespace link_api {

enum class ArbiterState : uint8_t {
    PrimaryActive     = 0, // Основний канал справний, повний потік
    PrimaryDegraded   = 1, // Початок завад/втрат: стиснення телеметрії
    Switching         = 2, // Процес перемикання та РЧ-комутації
    FallbackActive    = 3, // Робота на резервному каналі
    RecoveryEval      = 4, // Перевірка стабільності перед поверненням
    EmergencyAutonomy = 5  // Всі канали заглушено: активація Failsafe
};

} // namespace link_api
