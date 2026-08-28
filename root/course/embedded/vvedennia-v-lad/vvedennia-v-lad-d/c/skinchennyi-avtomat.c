typedef enum {
    ONBOARD_STATE_FACTORY_UNPROVISIONED = 0, // З коробки: IDevID готовий, мережеві налаштування відсутні
    ONBOARD_STATE_CHANNEL_ACTIVE        = 1, // Відкрито BLE/SoftAP, очікування клієнта
    ONBOARD_STATE_AUTHENTICATING        = 2, // Клієнт підключився, виконання PAKE-рукостискання
    ONBOARD_STATE_RECEIVING_CONFIG      = 3, // Канал зашифровано, прийом Wi-Fi/Cloud параметрів
    ONBOARD_STATE_NET_CONNECTING        = 4, // Спроба підключення до роутера (STA режим)
    ONBOARD_STATE_BOOTSTRAPPING_CLOUD   = 5, // Зв'язок є, запит CSR до хмари, верифікація Claiming
    ONBOARD_STATE_OPERATIONAL_CLAIMED   = 6, // LDevID записано, робота в парку, конфіг-канал вимкнено
    ONBOARD_STATE_ERROR_RECOVERY        = 7  // Помилка (хибний пароль тощо), надсилання звіту клієнту
} onboard_state_t;
