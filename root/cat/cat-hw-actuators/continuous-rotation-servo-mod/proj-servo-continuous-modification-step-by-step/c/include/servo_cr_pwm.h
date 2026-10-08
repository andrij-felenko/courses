#ifndef SERVO_CR_PWM_H
#define SERVO_CR_PWM_H

#include <stdint.h>
#include <stdbool.h>

/**
 * @file servo_cr_pwm.h
 * @brief Драйвер апаратного ШІМ-таймера для керування сервоприводом постійного обертання.
 *
 * Модуль реалізує керування швидкістю та напрямком обертання вала за допомогою
 * стандартизованого ШІМ-сигналу частотою 50 Гц (період 20 мс) з шириною імпульсу 1.0–2.0 мс.
 */

/* Фізичні та часові параметри керування ШІМ */
#define SERVO_CR_PWM_FREQ_HZ         50U     /**< Частота ШІМ-сигналу в Гц (період 20 мс) */
#define SERVO_CR_PERIOD_US           20000U  /**< Повний період ШІМ-сигналу в мікросекундах */

#define SERVO_CR_PULSE_MIN_US        1000U   /**< Імпульс максимальної швидкості проти годинникової стрілки (-100%) */
#define SERVO_CR_PULSE_NEUTRAL_US    1500U   /**< Базовий імпульс нейтрального стану / зупинки вала (1.5 мс) */
#define SERVO_CR_PULSE_MAX_US        2000U   /**< Імпульс максимальної швидкості за годинниковою стрілкою (+100%) */

#define SERVO_CR_SPEED_MIN_PCT       (-100.0f) /**< Мінімальне нормоване значення швидкості (100% реверс) */
#define SERVO_CR_SPEED_MAX_PCT       (100.0f)  /**< Максимальне нормоване значення швидкості (100% вперед) */

/**
 * @brief Структура регістрів апаратного таймера мікроконтролера (CMSIS TIM_TypeDef)
 */
typedef struct {
    volatile uint32_t CR1;   /**< Регістр керування 1 (Control Register 1) */
    volatile uint32_t CR2;   /**< Регістр керування 2 (Control Register 2) */
    volatile uint32_t SMCR;  /**< Регістр керування веденим режимом (Slave Mode) */
    volatile uint32_t DIER;  /**< Регістр дозволу переривань та DMA (Interrupt Enable) */
    volatile uint32_t SR;    /**< Регістр статусу прапорців (Status Register) */
    volatile uint32_t EGR;   /**< Регістр генерації подій (Event Generation) */
    volatile uint32_t CCMR1; /**< Регістр режиму захоплення/порівняння 1 (Channel 1 & 2) */
    volatile uint32_t CCMR2; /**< Регістр режиму захоплення/порівняння 2 (Channel 3 & 4) */
    volatile uint32_t CCER;  /**< Регістр дозволу виходів (Capture/Compare Enable) */
    volatile uint32_t CNT;   /**< Лічильник таймера (Counter Value) */
    volatile uint32_t PSC;   /**< Попередній дільник частоти (Prescaler) */
    volatile uint32_t ARR;   /**< Регістр автоперезавантаження (Auto-reload / Period) */
    volatile uint32_t CCR1;  /**< Регістр порівняння каналу 1 (Capture/Compare 1 / Duty) */
    volatile uint32_t CCR2;  /**< Регістр порівняння каналу 2 */
    volatile uint32_t CCR3;  /**< Регістр порівняння каналу 3 */
    volatile uint32_t CCR4;  /**< Регістр порівняння каналу 4 */
    volatile uint32_t BDTR;  /**< Регістр управління головним виходом (Break and Dead-time) */
} TIM_TypeDef;

/* Бітові маски керування регістром TIM_CR1 */
#define TIM_CR1_CEN       (1U << 0)  /**< Вмикання лічильника (Counter Enable) */
#define TIM_CR1_UDIS      (1U << 1)  /**< Заборона оновлення теневих регістрів */
#define TIM_CR1_URS       (1U << 2)  /**< Джерело події оновлення */
#define TIM_CR1_ARPE      (1U << 7)  /**< Буферизація регістра ARR (Auto-reload Preload Enable) */

/* Бітові маски керування регістром TIM_EGR */
#define TIM_EGR_UG        (1U << 0)  /**< Примусова генерація події оновлення (Update Generation) */

/* Бітові маски керування регістром TIM_CCMR1 */
#define TIM_CCMR1_OC1M_PWM1 (6U << 4) /**< Режим ШІМ 1 для каналу 1 (PWM Mode 1) */
#define TIM_CCMR1_OC1PE     (1U << 3) /**< Дозвіл буферизації CCR1 (Preload Enable) */

/* Бітові маски керування регістром TIM_CCER */
#define TIM_CCER_CC1E     (1U << 0)  /**< Вмикання виходу каналу 1 (Output Enable) */
#define TIM_CCER_CC1P     (1U << 1)  /**< Полярність виходу (0 = активний високий рівень) */

/* Бітові маски керування регістром TIM_BDTR */
#define TIM_BDTR_MOE      (1U << 15) /**< Головний дозвіл виходів (Main Output Enable) */

/**
 * @brief Структура налаштування таймера для сервоприводу
 */
typedef struct {
    TIM_TypeDef *timer_instance; /**< Вказівник на екземпляр апаратного таймера */
    uint32_t timer_clock_hz;    /**< Тактова частота таймера в Гц (наприклад, 72000000) */
    uint16_t initial_pulse_us;   /**< Початкова тривалість імпульсу в мкс (за замовчуванням 1500) */
    bool invert_direction;      /**< Прапорець інверсії напрямку обертання */
} servo_cr_pwm_config_t;

/**
 * @brief Ініціалізація апаратного таймера для формування ШІМ-сигналу.
 *
 * Налаштовує Prescaler для дискретності 1 мкс та ARR для періоду 20 мс (50 Гц).
 *
 * @param config Вказівник на структуру конфігурації.
 * @return 0 при успішному виконанні, -1 при недійсних параметрах.
 */
int servo_cr_pwm_init(const servo_cr_pwm_config_t *config);

/**
 * @brief Встановлення абсолютної тривалості керуючого імпульсу в мікросекундах.
 *
 * Безпосередньо оновлює регістр CCR1 таймера.
 *
 * @param pulse_us Тривалість імпульсу в діапазоні 1000..2000 мкс.
 * @return 0 при успіху, -1 якщо тривалість виходить за допустимі межі.
 */
int servo_cr_pwm_set_pulse_us(uint16_t pulse_us);

/**
 * @brief Встановлення нормованої швидкості та напрямку обертання вала.
 *
 * Перераховує відсотки (-100.0% .. +100.0%) у тривалість імпульсу (1000 .. 2000 мкс).
 *
 * @param speed_pct Задана швидкість у відсотках (-100.0f до +100.0f).
 * @return 0 при успіху, -1 при помилці.
 */
int servo_cr_pwm_set_speed(float speed_pct);

/**
 * @brief Отримання поточної тривалості імпульсу в мікросекундах.
 * @return Тривалість імпульсу в мкс (значення регістра CCR1).
 */
uint16_t servo_cr_pwm_get_pulse_us(void);

/**
 * @brief Отримання поточної встановленої нормованої швидкості (-100% .. +100%).
 * @return Поточна швидкість у відсотках.
 */
float servo_cr_pwm_get_speed(void);

/**
 * @brief Переведення сервоприводу у стан спокою (встановлення нейтрального імпульсу 1500 мкс).
 */
void servo_cr_pwm_stop(void);

#endif /* SERVO_CR_PWM_H */
