#ifndef PUMP_PWM_H
#define PUMP_PWM_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/**
 * @file pump_pwm.h
 * @brief Низькорівневий C-драйвер водяної помпи RS-360SH на основі апаратного ШІМ-таймера МК.
 *
 * Модуль реалізує пряму маніпуляцію реєстрами таймера (PSC, ARR, CCR),
 * неблокуючу плавну зміну обертів (Soft Start/Stop) для усунення пускових кидків
 * струму та захист від роботи в зоні заклинювання (нижче мінімального моменту).
 */

/* Фізичні та електричні константи водяної помпи RS-360SH */
#define RS360SH_NOMINAL_VOLTAGE_V        12.0f   /**< Номінальна напруга живлення двигуна помпи (В) */
#define RS360SH_DEFAULT_PWM_FREQ_HZ      10000U  /**< Базова частота ШІМ для відсутності акустичного шуму (10 кГц) */
#define RS360SH_MIN_OPERATIONAL_DUTY_PCT 20.0f   /**< Мінімальний коефіцієнт заповнення для подолання сухого тертя мембрани (%) */
#define RS360SH_MAX_OPERATIONAL_DUTY_PCT 100.0f  /**< Максимальний допустимий коефіцієнт заповнення ШІМ (%) */
#define RS360SH_MAX_FLOW_RATE_ML_MIN     1800.0f /**< Максимальна номінальна продуктивність помпи (1.8 л/хв = 1800 мл/хв) */
#define RS360SH_DEFAULT_RAMP_PCT_PER_SEC 40.0f   /**< Швидкість рампи за замовчуванням (% за секунду) */

/* Блоки масок та бітів для апаратних регістрів таймера МК (CMSIS style) */
#define TIMER_CR1_CEN                    (1U << 0) /**< Біт ввімкнення лічильника (Counter Enable) */
#define TIMER_CR1_ARPE                   (1U << 7) /**< Біт буферизації регістра ARR (Auto-reload preload enable) */
#define TIMER_CCMR1_OC1M_PWM1            (6U << 4) /**< Режим ШІМ 1 (Output Compare 1 Mode = 110b) */
#define TIMER_CCMR1_OC1PE                (1U << 3) /**< Біт буферизації регістра CCR1 (Preload enable) */
#define TIMER_CCER_CC1E                  (1U << 0) /**< Дозвіл генерації сигналу на каналі 1 (Channel 1 Enable) */
#define TIMER_BDTR_MOE                   (1U << 15)/**< Головний дозвіл виходів таймера (Main Output Enable) */

/**
 * @brief Апаратна структура регістрів таймера мікроконтролера (bare-metal CMSIS layout).
 */
typedef struct {
    volatile uint32_t CR1;   /**< Контрольний регістр 1 (керування лічильником) */
    volatile uint32_t CR2;   /**< Контрольний регістр 2 */
    volatile uint32_t SMCR;  /**< Регістр керування підпорядкованим режимом */
    volatile uint32_t DIER;  /**< Регістр дозволу переривань та DMA */
    volatile uint32_t SR;    /**< Регістр статусу прапорців */
    volatile uint32_t EGR;   /**< Регістр генерації подій */
    volatile uint32_t CCMR1; /**< Регістр вибору режиму каналів захвату/порівняння 1 і 2 */
    volatile uint32_t CCMR2; /**< Регістр вибору режиму каналів захвату/порівняння 3 і 4 */
    volatile uint32_t CCER;  /**< Регістр дозволу виходів порівняння */
    volatile uint32_t CNT;   /**< Регістр поточного лічильника таймера */
    volatile uint32_t PSC;   /**< Попередній дільник частоти тактування (Prescaler) */
    volatile uint32_t ARR;   /**< Регістр автоперезавантаження (Auto-reload, період ШІМ) */
    volatile uint32_t RCR;   /**< Регістр повторень */
    volatile uint32_t CCR1;  /**< Регістр порівняння каналу 1 (ширина імпульсу ШІМ) */
    volatile uint32_t CCR2;  /**< Регістр порівняння каналу 2 */
    volatile uint32_t CCR3;  /**< Регістр порівняння каналу 3 */
    volatile uint32_t CCR4;  /**< Регістр порівняння каналу 4 */
    volatile uint32_t BDTR;  /**< Регістр активації виходів та мертвих інтервалів */
} timer_reg_t;

/**
 * @brief Стан скінченного автомата драйвера помпи.
 */
typedef enum {
    PUMP_STATE_STOPPED = 0,    /**< Помпа повністю вимкнена (0% ШІМ) */
    PUMP_STATE_RAMPING,        /**< Виконується неблокуюча рампа розгону або гальмування */
    PUMP_STATE_RUNNING,        /**< Обертання на стабільній заданій швидкості */
    PUMP_STATE_EMERGENCY_STOP, /**< Аварійно вимкнена через захисний сигнал */
    PUMP_STATE_FAULT           /**< Виявлено помилку конфігурації або апаратури */
} pump_state_t;

/**
 * @brief Коди помилок виконання операцій C-драйвера.
 */
typedef enum {
    PUMP_OK = 0,               /**< Операцію виконано успішно */
    PUMP_ERR_NULL_PTR = -1,    /**< Передано нульовий вказівник */
    PUMP_ERR_INVALID_PARAM = -2,/**< Передано недопустиме значення параметра */
    PUMP_ERR_NOT_INIT = -3,    /**< Драйвер помпи не ініціалізовано */
    PUMP_ERR_HARDWARE_FAIL = -4,/**< Помилка розрахунку дільника апаратного таймера */
    PUMP_ERR_STALL_RISK = -5   /**< Попередження: зауважено ризик заклинювання двигуна */
} pump_err_t;

/**
 * @brief Структура первинної конфігурації помпи RS-360SH.
 */
typedef struct {
    timer_reg_t *timer_hw;         /**< Вказівник на блок регістрів апаратного таймера МК */
    uint32_t sys_clock_hz;         /**< Частота системного тактування периферичного таймера (Гц) */
    uint32_t pwm_freq_hz;          /**< Цільова частота ШІМ (Гц) */
    float min_operational_duty;    /**< Мінімальний робочий коефіцієнт заповнення (%) */
    float max_operational_duty;    /**< Максимальний допустимий коефіцієнт заповнення (%) */
    float ramp_rate_pct_per_sec;   /**< Швидкість програмної рампи (% за секунду) */
    float max_flow_ml_min;         /**< Максимальна витрата рідини при 100% ШІМ (мл/хв) */
} pump_config_t;

/**
 * @brief Дескриптор об'єкта драйвера керування помпою.
 */
typedef struct {
    pump_config_t config;          /**< Копія параметрів конфігурації */
    pump_state_t state;            /**< Поточний стан помпи */
    float current_duty_pct;        /**< Поточне значення коефіцієнта заповнення (0.0..100.0%) */
    float target_duty_pct;         /**< Цільове значення коефіцієнта заповнення (0.0..100.0%) */
    uint32_t last_update_ms;       /**< Часова мітка останнього обчислення рампи (мс) */
    double total_volume_ml;        /**< Накопичений об'єм прокачаної рідини (мл) */
    bool is_initialized;           /**< Прапорець завершення ініціалізації */
} pump_t;

/* --- Прототипи системного API C-драйвера --- */

/**
 * @brief Ініціалізація периферійного таймера МК та структури драйвера помпи.
 *
 * @param pump Вказівник на екземпляр дескриптора помпи.
 * @param config Вказівник на структуру параметрів ініціалізації.
 * @return PUMP_OK при успішному програмуванні регістрів PSC, ARR та CCMR1.
 */
pump_err_t pump_init(pump_t *pump, const pump_config_t *config);

/**
 * @brief Запит плавної зміни швидкості помпи (Soft Start / Soft Stop).
 *
 * Перевіряє безпечні межі та автоматично коригує запит нижче min_operational_duty
 * до безпечного порогу рушання або повного зупину (0%).
 *
 * @param pump Вказівник на екземпляр дескриптора.
 * @param target_duty_pct Бажаний коефіцієнт заповнення ШІМ у відсотках (0.0..100.0%).
 * @return PUMP_OK у разі успішного прийняття цілі.
 */
pump_err_t pump_set_speed(pump_t *pump, float target_duty_pct);

/**
 * @brief Негайне примусове оновлення значення ШІМ у регістрі CCR1 без використання рампи.
 *
 * @param pump Вказівник на дескриптор помпи.
 * @param duty_pct Коефіцієнт заповнення відсотків (0.0..100.0%).
 * @return PUMP_OK при успішному записі у регістр CCR1.
 */
pump_err_t pump_set_speed_immediate(pump_t *pump, float duty_pct);

/**
 * @brief Неблокуюча функція оновлення стану рампи та гідравлічної телеметрії.
 *
 * Повинна викликатися періодично у головному циклі або системному таймері (SysTick).
 *
 * @param pump Вказівник на дескриптор помпи.
 * @param current_time_ms Поточний системний час в мілісекундах.
 * @return PUMP_OK при успішній обробці тику.
 */
pump_err_t pump_update(pump_t *pump, uint32_t current_time_ms);

/**
 * @brief Плавне вимкнення помпи зі зменшенням обертів за профілем рампи.
 *
 * @param pump Вказівник на дескриптор помпи.
 * @return PUMP_OK при переході в режим плавного зупину.
 */
pump_err_t pump_stop(pump_t *pump);

/**
 * @brief Миттєва аварійна зупинка двигуна (атомарне очищення регістра CCR1 = 0).
 *
 * @param pump Вказівник на дескриптор помпи.
 * @return PUMP_OK при обнуленні ШІМ-виходу.
 */
pump_err_t pump_emergency_stop(pump_t *pump);

/**
 * @brief Отримання поточного коефіцієнта заповнення ШІМ (0.0..100.0%).
 */
float pump_get_current_speed(const pump_t *pump);

/**
 * @brief Обчислення миттєвої подачі рідини водяною помпою (мл/хв).
 */
float pump_get_estimated_flow_ml_min(const pump_t *pump);

/**
 * @brief Отримання сумарного накопиченого об'єму перекачаної рідини (мл).
 */
double pump_get_total_volume_ml(const pump_t *pump);

/**
 * @brief Зчитування поточного стану скінченного автомата помпи.
 */
pump_state_t pump_get_state(const pump_t *pump);

/**
 * @brief Перетворення коду помилки у текстовий рядок українською мовою.
 */
const char* pump_err_to_str(pump_err_t err);

#endif /* PUMP_PWM_H */
