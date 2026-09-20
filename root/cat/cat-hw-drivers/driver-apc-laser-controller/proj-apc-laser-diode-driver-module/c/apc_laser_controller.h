#ifndef APC_LASER_CONTROLLER_H
#define APC_LASER_CONTROLLER_H

#include <stdint.h>
#include <stdbool.h>

/**
 * @file apc_laser_controller.h
 * @brief Драйвер нижнього рівня для керування лазерним діодом у режимі APC.
 *
 * Модуль забезпечує конфігурацію периферійних пристроїв МК (ЦАП, АЦП, GPIO Enable),
 * алгоритм плавного пуску (soft start), стабілізацію потужності через зворотний зв'язок
 * від моніторного фотодіода та миттєвий програмно-апаратний захист від перевантаження.
 */

/**
 * @brief Статуси виконання та коди помилок драйвера APC.
 */
typedef enum {
    APC_OK = 0,                 /**< Операцію виконано успішно */
    APC_ERROR_INVALID_PARAM,    /**< Некоректні вхідні параметри конфігурації */
    APC_ERROR_OVERCURRENT,      /**< Перевищено поріг струму моніторного фотодіода (аварія) */
    APC_ERROR_NOT_INITIALIZED,  /**< Драйвер не було ініціалізовано */
    APC_ERROR_HARDWARE_FAULT    /**< Збій периферійного модуля МК */
} apc_status_t;

/**
 * @brief Робочий стан контролера лазерного діода.
 */
typedef enum {
    APC_STATE_DISABLED = 0,     /**< Лазер вимкнено (Enable = LOW, ЦАП = 0) */
    APC_STATE_SOFT_START,       /**< Виконується процедура плавного пуску */
    APC_STATE_RUNNING,          /**< Активна стабілізація оптичної потужності (APC) */
    APC_STATE_FAULT             /**< Аварійний стан через спрацювання захисту */
} apc_state_t;

/**
 * @brief Конфігурація зв'язаної апаратної периферії мікроконтролера.
 */
typedef struct {
    uint8_t dac_channel;        /**< Канал ЦАП керування струмом накачки */
    uint8_t adc_pd_channel;     /**< Канал АЦП моніторного фотодіода */
    uint8_t gpio_enable_port;   /**< Порт GPIO ліній Enable */
    uint16_t gpio_enable_pin;   /**< Пін GPIO керування силовим ключем Enable */
} apc_hardware_config_t;

/**
 * @brief Конфігураційні параметри та порогові значення APC.
 */
typedef struct {
    apc_hardware_config_t hw;   /**< Параметри зв'язку з периферією */
    uint16_t max_pd_adc_raw;    /**< Порогове значення АЦП фотодіода для захисту */
    uint16_t target_pd_adc_raw; /**< Цільове значення АЦП фотодіода (бажана потужність) */
    uint16_t dac_max_limit;     /**< Абсолютний ліміт значення ЦАП (обмеження струму) */
    uint16_t soft_start_step;   /**< Крок збільшення ЦАП при плавній запитці */
    uint32_t soft_start_delay_ms;/**< Затримка між кроками плавного пуску (мс) */
    uint16_t kp_gain;           /**< Пропорційний коефіцієнт регулятора */
    uint16_t ki_gain;           /**< Інтегральний коефіцієнт регулятора */
} apc_config_t;

/**
 * @brief Дескриптор внутрішнього стану драйвера.
 */
typedef struct {
    apc_config_t config;        /**< Поточні налаштування контролера */
    apc_state_t state;          /**< Робочий стан драйвера */
    uint16_t current_dac_val;   /**< Поточне значення виходу ЦАП */
    uint16_t last_adc_raw;      /**< Останній відлік з АЦП фотодіода */
    int32_t integral_error;     /**< Накопичена помилка для І-компоненти ПІ-регулятора */
    apc_status_t last_error;    /**< Код останньої зареєстрованої помилки */
    bool is_initialized;        /**< Прапор готовності драйвера до роботи */
} apc_driver_t;

/* Прототипи функцій API */

/**
 * @brief Ініціалізація периферійних модулів та структури драйвера.
 * @param driver Вказівник на екземпляр драйвера.
 * @param config Налаштування та порогові значення.
 * @return APC_OK при успіху або відповідний код помилки.
 */
apc_status_t apc_laser_init(apc_driver_t *driver, const apc_config_t *config);

/**
 * @brief Виконання покрокового плавного пуску (Soft Start) для запобігання кидаткам струму.
 * @param driver Вказівник на екземпляр драйвера.
 * @return APC_OK при виході на робочу потужність, або APC_ERROR_OVERCURRENT.
 */
apc_status_t apc_laser_soft_start(apc_driver_t *driver);

/**
 * @brief Оновлення контуру регулювання потужності APC в замкненому циклі.
 * @param driver Вказівник на екземпляр драйвера.
 * @return APC_OK або код помилки/аварії.
 */
apc_status_t apc_laser_update_apc(apc_driver_t *driver);

/**
 * @brief Перевірка показників фотодіода на перевищення безпечної межі.
 * @param driver Вказівник на екземпляр драйвера.
 * @return true — показники у нормі, false — виявлено небезпечне перевищення.
 */
bool apc_laser_check_protection(apc_driver_t *driver);

/**
 * @brief Негайне примусове вимкнення силового ключа та скидання ЦАП.
 * @param driver Вказівник на екземпляр драйвера.
 * @return APC_OK після безпечної зупинки.
 */
apc_status_t apc_laser_disable(apc_driver_t *driver);

/**
 * @brief Задання нового цільового рівня оптичної потужності.
 * @param driver Вказівник на екземпляр драйвера.
 * @param target_adc_raw Нове значення відліку АЦП фотодіода.
 * @return APC_OK або APC_ERROR_INVALID_PARAM при перевищенні захисного порогу.
 */
apc_status_t apc_laser_set_target(apc_driver_t *driver, uint16_t target_adc_raw);

/**
 * @brief Отримання поточного стану автомата драйвера.
 * @param driver Вказівник на екземпляр драйвера.
 * @return Значення enum apc_state_t.
 */
apc_state_t apc_laser_get_state(const apc_driver_t *driver);

#endif /* APC_LASER_CONTROLLER_H */
