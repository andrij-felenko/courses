#ifndef LASER_DRIVER_H
#define LASER_DRIVER_H

/**
 * @file laser_driver.h
 * @brief Заголовний файл низькорівневого драйвера лазерного модуля.
 *
 * Драйвер забезпечує апаратне мікросекундне стробування (One-Pulse Mode),
 * синхронізацію через зовнішні переривання EXTI, захист від COD і перегріву,
 * медіанну фільтрацію сигналів АЦП та неблокувальний кінцевий автомат безпеки.
 */

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/** @brief Розмір вікна медіанного фільтра вимірювань АЦП. */
#define LASER_MEDIAN_WINDOW_SIZE 5

/**
 * @brief Стани кінцевого автомата (FSM) безпеки лазерного модуля.
 */
typedef enum {
    LASER_STATE_DISABLED = 0, /**< Модуль вимкнено або розімкнено інтерлок */
    LASER_STATE_READY,        /**< Готовий до випромінювання, очікує строб-сигнал */
    LASER_STATE_STROBING,     /**< Активне імпульсне стробування (One-Pulse) */
    LASER_STATE_CONTINUOUS,   /**< Неперервне випромінювання з ШІМ-регулюванням */
    LASER_STATE_FAULT         /**< Аварійний стан: апаратне блокування випромінювання */
} laser_state_t;

/**
 * @brief Коди апаратних та експлуатаційних помилок модуля.
 */
typedef enum {
    LASER_FAULT_NONE = 0,        /**< Помилок немає */
    LASER_FAULT_OVERTEMP,        /**< Перевищення критичної температури кристала */
    LASER_FAULT_OVERPOWER_COD,   /**< Перевищення оптичної потужності (загроза COD) */
    LASER_FAULT_INTERLOCK_OPEN,  /**< Розімкнено зовнішнє коло безпеки (інтерлок) */
    LASER_FAULT_WATCHDOG_TIMEOUT,/**< Спрацював апаратний сторожовий таймер випромінювання */
    LASER_FAULT_ADC_UNSTABLE     /**< Збій або неприпустимі шуми фотодетектора */
} laser_fault_t;

/**
 * @brief Режим оптичного випромінювання.
 */
typedef enum {
    LASER_MODE_STROBE_OPM = 0, /**< Одиночний мікросекундний імпульс на кадр камери */
    LASER_MODE_CONTINUOUS_PWM  /**< Неперервний високочастотний ШІМ */
} laser_mode_t;

/**
 * @brief Апаратні регістри таймера (CMSIS-сумісна структура TIM_TypeDef).
 */
typedef struct {
    volatile uint32_t CR1;   /**< Регістр керування 1: біт OPM (One-Pulse), біт CEN */
    volatile uint32_t CR2;   /**< Регістр керування 2: конфігурація тригера master/slave */
    volatile uint32_t SMCR;  /**< Slave mode: вибір зовнішнього входу тригера EXTI */
    volatile uint32_t DIER;  /**< Дозвіл переривань таймера */
    volatile uint32_t SR;    /**< Регістр статусу прапорців подій */
    volatile uint32_t EGR;   /**< Генерація програмних подій оновлення */
    volatile uint32_t CCMR1; /**< Конфігурація каналу порівняння: режим ШІМ */
    volatile uint32_t CCER;  /**< Дозвіл виходу на затвор силового ключа лазера */
    volatile uint32_t CNT;   /**< Поточний лічильник тактових імпульсів */
    volatile uint32_t PSC;   /**< Дільник тактової частоти шини таймера */
    volatile uint32_t ARR;   /**< Регістр автоперезавантаження (тривалість періоду) */
    volatile uint32_t CCR1;  /**< Регістр порівняння (тривалість активного імпульсу) */
} laser_hw_timer_t;

/**
 * @brief Параметри конфігурації та обмежень безпеки.
 */
typedef struct {
    uint32_t timer_clock_hz;        /**< Тактова частота таймера (наприклад, 84 000 000 Гц) */
    uint32_t default_strobe_us;     /**< Тривалість стробу за замовчуванням (мкс) */
    uint32_t pwm_frequency_hz;      /**< Частота ШІМ у неперервному режимі (Гц) */
    uint16_t pwm_duty_permille;     /**< Заповнення ШІМ у проміле (0..1000) */
    float max_temp_celsius;         /**< Поріг аварійного вимкнення за температурою */
    uint16_t max_photodiode_raw;    /**< Поріг детектора фотодіода (захист від COD) */
    uint16_t min_photodiode_raw;    /**< Мінімальний поріг відгуку (контроль обриву діода) */
    uint32_t watchdog_timeout_ms;   /**< Максимальний час неперервного світіння (мс) */
} laser_config_t;

/**
 * @brief Поточна телеметрія стану модуля.
 */
typedef struct {
    float filtered_temperature_c;   /**< Відфільтрована температура кристала (град. C) */
    uint16_t filtered_photodiode_raw;/**< Відфільтроване значення фотодіода (код АЦП) */
    uint32_t pulse_count;           /**< Лічильник згенерованих строб-імпульсів */
    bool interlock_closed;          /**< Стан контуру безпеки (true = замкнено) */
} laser_telemetry_t;

/**
 * @brief Головний дескриптор екземпляра драйвера лазера.
 */
typedef struct {
    laser_hw_timer_t *timer;        /**< Вказівник на апаратні регістри таймера */
    laser_config_t config;          /**< Робоча конфігурація та пороги */
    laser_state_t state;            /**< Поточний стан кінцевого автомата */
    laser_fault_t fault_code;       /**< Код зафіксованої помилки */
    laser_mode_t current_mode;      /**< Активний режим випромінювання */

    /* Буфери ковзного вікна медіанного фільтра АЦП */
    uint16_t pd_history[LASER_MEDIAN_WINDOW_SIZE];
    uint16_t temp_history[LASER_MEDIAN_WINDOW_SIZE];
    uint8_t filter_index;

    /* Телеметрія та лічильники */
    laser_telemetry_t telemetry;
    uint32_t emission_start_tick_ms;/**< Час увімкнення для контролю watchdog */
} laser_device_t;

/* --- Прототипи функцій драйвера --- */

/**
 * @brief Ініціалізація структури драйвера та конфігурація апаратної периферії.
 * @param dev Вказівник на дескриптор лазера.
 * @param timer_regs Вказівник на базову адресу регістрів таймера.
 * @param cfg Вказівник на структуру конфігурації.
 * @return true при успішній ініціалізації, false при невалідних параметрах.
 */
bool laser_driver_init(laser_device_t *dev, laser_hw_timer_t *timer_regs, const laser_config_t *cfg);

/**
 * @brief Налаштування таймера в режим One-Pulse Mode (одиночний мікросекундний імпульс).
 * @param dev Вказівник на дескриптор.
 * @param duration_us Тривалість спалаху лазера в мікросекундах.
 */
void laser_driver_configure_one_pulse(laser_device_t *dev, uint32_t duration_us);

/**
 * @brief Налаштування таймера у високочастотний режим ШІМ для регулювання яскравості.
 * @param dev Вказівник на дескриптор.
 * @param frequency_hz Частота ШІМ (Гц).
 * @param duty_permille Коефіцієнт заповнення (0..1000).
 */
void laser_driver_configure_pwm(laser_device_t *dev, uint32_t frequency_hz, uint16_t duty_permille);

/**
 * @brief Обробник зовнішнього переривання EXTI (строб від камери машинного зору).
 * Викликається у контексті ISR з мінімальним детермінованим джитером.
 * @param dev Вказівник на дескриптор.
 */
void laser_driver_on_exti_trigger_isr(laser_device_t *dev);

/**
 * @brief Оновлення буферів АЦП новими відліками та медіанна фільтрація.
 * @param dev Вказівник на дескриптор.
 * @param raw_photodiode Сирий відлік каналу фотодіода (0..4095).
 * @param raw_temp_mv Напруга на термісторі в мілівольтах.
 */
void laser_driver_update_adc_samples(laser_device_t *dev, uint16_t raw_photodiode, uint16_t raw_temp_mv);

/**
 * @brief Неблокувальний крок кінцевого автомата безпеки (FSM).
 * Викликається у головному суперциклі з періодом 1..5 мс.
 * @param dev Вказівник на дескриптор.
 * @param current_tick_ms Поточний системний час у мілісекундах.
 */
void laser_driver_process_fsm(laser_device_t *dev, uint32_t current_tick_ms);

/**
 * @brief Керування зовнішнім колом блокування (інтерлоком).
 * @param dev Вказівник на дескриптор.
 * @param is_closed true — контур замкнено (дозволено), false — розімкнено.
 */
void laser_driver_set_interlock(laser_device_t *dev, bool is_closed);

/**
 * @brief Аварійне апаратне відключення випромінювання та перехід у стан FAULT.
 * @param dev Вказівник на дескриптор.
 * @param fault Причина аварійної зупинки.
 */
void laser_driver_emergency_shutdown(laser_device_t *dev, laser_fault_t fault);

/**
 * @brief Скидання аварійного стану після усунення першопричини.
 * @param dev Вказівник на дескриптор.
 * @return true, якщо скидання дозволено, false, якщо аварійні умови зберігаються.
 */
bool laser_driver_reset_fault(laser_device_t *dev);

/**
 * @brief Отримання поточного стану FSM.
 */
laser_state_t laser_driver_get_state(const laser_device_t *dev);

/**
 * @brief Отримання копії структури поточної телеметрії.
 */
void laser_driver_get_telemetry(const laser_device_t *dev, laser_telemetry_t *out_telemetry);

#ifdef __cplusplus
}
#endif

#endif /* LASER_DRIVER_H */
