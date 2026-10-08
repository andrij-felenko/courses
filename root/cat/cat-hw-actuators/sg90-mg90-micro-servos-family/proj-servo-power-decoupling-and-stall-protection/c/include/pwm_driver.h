#ifndef PWM_DRIVER_H
#define PWM_DRIVER_H

#include <stdint.h>
#include <stdbool.h>

/**
 * @file pwm_driver.h
 * @brief Низькорівневий драйвер ШІМ для керування сервоприводами родини Tower Pro.
 *
 * Забезпечує формування 50 Гц ШІМ-сигналу (період 20 мс) з мікросекундною
 * точністю тривалості імпульсу та можливістю апаратного відключення виходу (detach).
 */

#define PWM_FREQ_HZ           50U     /**< Частота керуючого сигналу ШІМ (Гц) */
#define PWM_PERIOD_US         20000U  /**< Повний період ШІМ-сигналу в мікросекундах (20 мс) */
#define PWM_PULSE_MIN_US      500U    /**< Абсолютний мінімум тривалості імпульсу (мкс) */
#define PWM_PULSE_MAX_US      2500U   /**< Абсолютний максимум тривалості імпульсу (мкс) */
#define PWM_PULSE_NEUTRAL_US  1500U   /**< Нейтральне значення тривалості імпульсу (мкс) */

/**
 * @brief Структура регістрів апаратного таймера мікроконтролера (CMSIS-подібна)
 */
typedef struct {
    volatile uint32_t CR1;   /**< Регістр керування 1 (Control Register 1) */
    volatile uint32_t CR2;   /**< Регістр керування 2 (Control Register 2) */
    volatile uint32_t SMCR;  /**< Регістр керування веденим режимом */
    volatile uint32_t DIER;  /**< Регістр дозволу переривань та DMA */
    volatile uint32_t SR;    /**< Регістр статусу прапорців */
    volatile uint32_t EGR;   /**< Регістр генерації подій */
    volatile uint32_t CCMR1; /**< Регістр режиму захоплення/порівняння 1 */
    volatile uint32_t CCMR2; /**< Регістр режиму захоплення/порівняння 2 */
    volatile uint32_t CCER;  /**< Регістр дозволу виходів захоплення/порівняння */
    volatile uint32_t CNT;   /**< Лічильник таймера */
    volatile uint32_t PSC;   /**< Попередній дільник частоти (Prescaler) */
    volatile uint32_t ARR;   /**< Регістр автоперезавантаження (Auto-reload) */
    volatile uint32_t CCR1;  /**< Регістр порівняння каналу 1 */
    volatile uint32_t CCR2;  /**< Регістр порівняння каналу 2 */
    volatile uint32_t CCR3;  /**< Регістр порівняння каналу 3 */
    volatile uint32_t CCR4;  /**< Регістр порівняння каналу 4 */
    volatile uint32_t BDTR;  /**< Регістр керування виходами */
} TIM_TypeDef;

/* Бітові маски керування регістрами таймера */
#define TIM_CR1_CEN          (1U << 0)  /**< Вмикання лічильника */
#define TIM_CR1_ARPE         (1U << 7)  /**< Буферизація регістра ARR */
#define TIM_EGR_UG           (1U << 0)  /**< Генерація події оновлення */
#define TIM_CCMR1_OC1M_PWM1  (6U << 4)  /**< Режим ШІМ 1 для каналу 1 */
#define TIM_CCMR1_OC1PE      (1U << 3)  /**< Дозвіл буферизації CCR1 */
#define TIM_CCER_CC1E        (1U << 0)  /**< Дозвіл виходу каналу 1 */
#define TIM_CCER_CC2E        (1U << 4)  /**< Дозвіл виходу каналу 2 */
#define TIM_CCER_CC3E        (1U << 8)  /**< Дозвіл виходу каналу 3 */
#define TIM_CCER_CC4E        (1U << 12) /**< Дозвіл виходу каналу 4 */

/**
 * @brief Описовий контекст низькорівневого ШІМ-драйвера
 */
typedef struct {
    TIM_TypeDef *timer;       /**< Вказівник на блок регістрів апаратного таймера */
    uint32_t channel;         /**< Номер каналу ШІМ (1, 2, 3 або 4) */
    uint32_t timer_clock_hz;  /**< Тактова частота таймера (Гц) */
    uint16_t current_pulse_us;/**< Поточна тривалість керуючого імпульсу (мкс) */
    bool is_enabled;          /**< Прапорець активності генерації ШІМ-сигналу */
} pwm_driver_t;

/**
 * @brief Ініціалізує низькорівневий ШІМ-драйвер для вказаного таймера та каналу.
 * @param driver Вказівник на екземпляр ШІМ-драйвера
 * @param timer Вказівник на регістри апаратного таймера
 * @param channel Номер каналу (1..4)
 * @param clock_hz Вхідна тактова частота таймера в Гц
 * @return 0 при успіху, -1 при некоректних параметрах
 */
int pwm_driver_init(pwm_driver_t *driver, TIM_TypeDef *timer, uint32_t channel, uint32_t clock_hz);

/**
 * @brief Встановлює ширину імпульсу в мікросекундах.
 * @param driver Вказівник на екземпляр ШІМ-драйвера
 * @param pulse_us Тривалість імпульсу (обмежується в межах 500..2500 мкс)
 * @return 0 при успіху, -1 при некоректному вказівнику
 */
int pwm_driver_set_pulse_us(pwm_driver_t *driver, uint16_t pulse_us);

/**
 * @brief Негайно вимикає генерацію ШІМ-сигналу на апаратному рівні (detach).
 * @param driver Вказівник на екземпляр ШІМ-драйвера
 * @return 0 при успіху, -1 при помилці
 */
int pwm_driver_detach(pwm_driver_t *driver);

/**
 * @brief Відновлює генерацію ШІМ-сигналу з останньою встановленою тривалістю імпульсу (attach).
 * @param driver Вказівник на екземпляр ШІМ-драйвера
 * @return 0 при успіху, -1 при помилці
 */
int pwm_driver_attach(pwm_driver_t *driver);

/**
 * @brief Перевіряє, чи активний вихід ШІМ-сигналу.
 * @param driver Вказівник на екземпляр ШІМ-драйвера
 * @return true, якщо ШІМ увімкнено; false, якщо вимкнено або driver == NULL
 */
bool pwm_driver_is_enabled(const pwm_driver_t *driver);

/**
 * @brief Повертає поточну встановлену тривалість імпульсу в мікросекундах.
 * @param driver Вказівник на екземпляр ШІМ-драйвера
 * @return Тривалість імпульсу в мкс або 0 при помилці
 */
uint16_t pwm_driver_get_pulse_us(const pwm_driver_t *driver);

#endif /* PWM_DRIVER_H */
