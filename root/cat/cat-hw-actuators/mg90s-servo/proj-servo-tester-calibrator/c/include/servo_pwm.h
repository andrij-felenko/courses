#ifndef SERVO_PWM_H
#define SERVO_PWM_H

#include <stdint.h>
#include <stdbool.h>

/**
 * @file servo_pwm.h
 * @brief Низькорівневий драйвер ШІМ для мікросервопривода MG90S V2.
 *
 * Описує інтерфейс конфігурації апаратного таймера мікроконтролера
 * для формування сигналу з частотою 50 Гц та шириною імпульсу 1000..2000 мкс.
 */

/* Фізичні константи керування MG90S V2 */
#define SERVO_PWM_FREQ_HZ         50U     /**< Частота керуючого ШІМ (період 20 мс / 20000 мкс) */
#define SERVO_PERIOD_US           20000U  /**< Повний період ШІМ-сигналу в мікросекундах */
#define SERVO_PULSE_MIN_US        1000U   /**< Мінімальна тривалість імпульсу (0 градусів) */
#define SERVO_PULSE_CENTER_US     1500U   /**< Нейтральне положення імпульсу (90 градусів) */
#define SERVO_PULSE_MAX_US        2000U   /**< Максимальна тривалість імпульсу (180 градусів) */

#define SERVO_ANGLE_MIN_DEG       0.0f    /**< Мінімальний кут повороту вала в градусах */
#define SERVO_ANGLE_MAX_DEG       180.0f  /**< Максимальний кут повороту вала в градусах */

/**
 * @brief Структура регістрів таймера мікроконтролера (CMSIS-подібне представлення)
 */
typedef struct {
    volatile uint32_t CR1;   /**< Регістр керування 1 (Control Register 1) */
    volatile uint32_t CR2;   /**< Регістр керування 2 (Control Register 2) */
    volatile uint32_t SMCR;  /**< Регістр керування веденим режимом (Slave Mode) */
    volatile uint32_t DIER;  /**< Регістр дозволу переривань та DMA */
    volatile uint32_t SR;    /**< Регістр статусу прапорців (Status Register) */
    volatile uint32_t EGR;   /**< Регістр генерації подій (Event Generation Register) */
    volatile uint32_t CCMR1; /**< Регістр режиму захоплення/порівняння 1 */
    volatile uint32_t CCMR2; /**< Регістр режиму захоплення/порівняння 2 */
    volatile uint32_t CCER;  /**< Регістр дозволу виходів захоплення/порівняння */
    volatile uint32_t CNT;   /**< Лічильник таймера (Counter Register) */
    volatile uint32_t PSC;   /**< Попередній дільник частоти (Prescaler) */
    volatile uint32_t ARR;   /**< Регістр автоперезавантаження (Auto-reload Register) */
    volatile uint32_t CCR1;  /**< Регістр порівняння каналу 1 (Capture/Compare 1) */
    volatile uint32_t CCR2;  /**< Регістр порівняння каналу 2 */
    volatile uint32_t CCR3;  /**< Регістр порівняння каналу 3 */
    volatile uint32_t CCR4;  /**< Регістр порівняння каналу 4 */
    volatile uint32_t BDTR;  /**< Регістр управління виходами та мертвим часом */
} TIM_TypeDef;

/* Бітові маски регістру TIM_CR1 */
#define TIM_CR1_CEN       (1U << 0)  /**< Дозвіл роботи лічильника (Counter Enable) */
#define TIM_CR1_UDIS      (1U << 1)  /**< Заборона оновлення (Update Disable) */
#define TIM_CR1_URS       (1U << 2)  /**< Джерело запиту оновлення (Update Request Source) */
#define TIM_CR1_ARPE      (1U << 7)  /**< Буферизація регістра ARR (Auto-reload Preload) */

/* Бітові маски регістру TIM_EGR */
#define TIM_EGR_UG        (1U << 0)  /**< Генерація події оновлення (Update Generation) */

/* Бітові маски регістру TIM_CCMR1 */
#define TIM_CCMR1_OC1M_PWM1 (6U << 4) /**< Режим ШІМ 1 для каналу 1 (PWM mode 1) */
#define TIM_CCMR1_OC1PE     (1U << 3) /**< Дозвіл попереднього завантаження CCR1 (Preload Enable) */

/* Бітові маски регістру TIM_CCER */
#define TIM_CCER_CC1E     (1U << 0)  /**< Увімкнення виходу каналу 1 (Channel 1 Output Enable) */
#define TIM_CCER_CC1P     (1U << 1)  /**< Полярність сигналу каналу 1 (Active High/Low) */

/**
 * @brief Конфігураційна структура для ініціалізації ШІМ-драйвера
 */
typedef struct {
    uint32_t timer_clock_hz; /**< Вхідна тактова частота апаратного таймера (Гц) */
    uint16_t initial_pulse_us;/**< Початкова тривалість імпульсу (мкс) */
    bool invert_polarity;    /**< Прапорець інверсії полярності вихідного імпульсу */
} servo_pwm_config_t;

/* Прототипи функцій API */

/**
 * @brief Ініціалізує апаратний таймер для генерації ШІМ-сигналу сервопривода MG90S V2.
 * @param config Вказівник на структуру конфігурації
 * @return 0 при успішній ініціалізації, -1 при некоректних параметрах
 */
int servo_pwm_init(const servo_pwm_config_t *config);

/**
 * @brief Встановлює тривалість імпульсу керування в мікросекундах.
 * @param pulse_us Тривалість імпульсу (обмежується в межах 1000..2000 мкс)
 * @return 0 у разі успіху, -1 у разі помилки або виходу за межі
 */
int servo_pwm_set_pulse_us(uint16_t pulse_us);

/**
 * @brief Установлює кут повороту вала сервопривода в градусах.
 * @param angle_deg Кут повороту (0.0 .. 180.0 градусів)
 * @return 0 у разі успіху, -1 у разі виходу за допустимий діапазон
 */
int servo_pwm_set_angle(float angle_deg);

/**
 * @brief Повертає поточну встановлену тривалість імпульсу у мікросекундах.
 * @return Поточна тривалість імпульсу в мкс
 */
uint16_t servo_pwm_get_current_pulse_us(void);

/**
 * @brief Повертає поточний розрахований кут у градусах.
 * @return Поточний кут вала в градусах (0.0..180.0)
 */
float servo_pwm_get_current_angle(void);

/**
 * @brief Вмикає або вимикає генерацію ШІМ-сигналу на вихідній ніжці.
 * @param enable true для ввімкнення, false для вимкнення
 */
void servo_pwm_enable(bool enable);

/**
 * @brief Отримання вказівника на об'єкт регістрів таймера (для діагностики та низкорівневих перевірок).
 * @return Вказівник на структуру TIM_TypeDef
 */
TIM_TypeDef *servo_pwm_get_timer_instance(void);

#endif /* SERVO_PWM_H */
