enum class OnboardState : std::uint8_t {
    FactoryUnprovisioned = 0, // З коробки: IDevID готовий, мережеві налаштування відсутні
    ChannelActive        = 1, // Відкрито BLE/SoftAP, очікування клієнта
    Authenticating       = 2, // Клієнт підключився, виконання PAKE-рукостискання
    ReceivingConfig      = 3, // Канал зашифровано, прийом Wi-Fi/Cloud параметрів
    NetConnecting        = 4, // Спроба підключення до роутера (STA режим)
    BootstrappingCloud   = 5, // Зв'язок є, запит CSR до хмари, верифікація Claiming
    OperationalClaimed   = 6, // LDevID записано, робота в парку, конфіг-канал вимкнено
    ErrorRecovery        = 7  // Помилка (хибний пароль тощо), надсилання звіту клієнту
};
