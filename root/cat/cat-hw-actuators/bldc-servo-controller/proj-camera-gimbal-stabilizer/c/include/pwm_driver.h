#ifndef PWM_DRIVER_H
#define PWM_DRIVER_H

#include <stdint.h>
#include <stdbool.h>

/**
 * @file pwm_driver.h
 * @brief Драйвер трифазного комплементарного ШІМ із вирівнюванням по центру та dead-time.
 */

/* Структура регістрів апаратного таймера (стиль CMSIS для MCU) */
typedef struct {
    volatile uint32_t CR1;   /**< Control register 1 */
    volatile uint32_t CR2;   /**< Control register 2 */
    volatile uint32_t SMCR;  /**< Slave mode control register */
    volatile uint32_t DIER;  /**< DMA/Interrupt enable register */
    volatile uint32_t SR;    /**< Status register */
    volatile uint32_t EGR;   /**< Event generation register */
    volatile uint32_t CCMR1; /**< Capture/compare mode register 1 */
    volatile uint32_t CCMR2; /**< Capture/compare mode register 2 */
    volatile uint32_t CCER;  /**< Capture/compare enable register */
    volatile uint32_t CNT;   /**< Counter register */
    volatile uint32_t PSC;   /**< Prescaler register */
    volatile uint32_t ARR;   /**< Auto-reload register */
    volatile uint32_t RCR;   /**< Repetition counter register */
    volatile uint32_t CCR1;  /**< Capture/compare register 1 (Фаза A) */
    volatile uint32_t CCR2;  /**< Capture/compare register 2 (Фаза B) */
    volatile uint32_t CCR3;  /**< Capture/compare register 3 (Фаза C) */
    volatile uint32_t CCR4;  /**< Capture/compare register 4 */
    volatile uint32_t BDTR;  /**< Break and dead-time register */
    volatile uint32_t DSER;  /**< Driver status enable register */
} TIM_TypeDef;

/* Макроси бітів регістру TIM_CR1 */
#define TIM_CR1_CEN          (1U << 0)  /**< Counter enable */
#define TIM_CR1_UDIS         (1U << 1)  /**< Update disable */
#define TIM_CR1_URS          (1U << 2)  /**< Update request source */
#define TIM_CR1_ARPE         (1U << 7)  /**< Auto-reload preload enable */
#define TIM_CR1_CMS_MASK     (3U << 5)  /**< Center-aligned mode selection mask */
#define TIM_CR1_CMS_CENTER1  (1U << 5)  /**< Center-aligned mode 1 (Mode 1 up/down) */

/* Макроси бітів регістрів TIM_CCMR1 та TIM_CCMR2 */
#define TIM_CCMR_OC1M_PWM1   (6U << 4)  /**< Output Compare 1 Mode: PWM mode 1 */
#define TIM_CCMR_OC1PE       (1U << 3)  /**< Output Compare 1 Preload enable */
#define TIM_CCMR_OC2M_PWM1   (6U << 12) /**< Output Compare 2 Mode: PWM mode 1 */
#define TIM_CCMR_OC2PE       (1U << 11) /**< Output Compare 2 Preload enable */
#define TIM_CCMR_OC3M_PWM1   (6U << 4)  /**< Output Compare 3 Mode: PWM mode 1 */
#define TIM_CCMR_OC3PE       (1U << 3)  /**< Output Compare 3 Preload enable */

/* Макроси бітів регістру TIM_CCER */
#define TIM_CCER_CC1E        (1U << 0)  /**< Channel 1 output enable (A) */
#define TIM_CCER_CC1NE       (1U << 2)  /**< Channel 1 complementary output enable (A_N) */
#define TIM_CCER_CC1P        (1U << 1)  /**< Channel 1 output polarity */
#define TIM_CCER_CC1NP       (1U << 3)  /**< Channel 1 complementary output polarity */

#define TIM_CCER_CC2E        (1U << 4)  /**< Channel 2 output enable (B) */
#define TIM_CCER_CC2NE       (1U << 6)  /**< Channel 2 complementary output enable (B_N) */
#define TIM_CCER_CC2P        (1U << 5)  /**< Channel 2 output polarity */
#define TIM_CCER_CC2NP       (1U << 7)  /**< Channel 2 complementary output polarity */

#define TIM_CCER_CC3E        (1U << 8)  /**< Channel 3 output enable (C) */
#define TIM_CCER_CC3NE       (1U << 10) /**< Channel 3 complementary output enable (C_N) */
#define TIM_CCER_CC3P        (1U << 9)  /**< Channel 3 output polarity */
#define TIM_CCER_CC3NP       (1U << 11) /**< Channel 3 complementary output polarity */

/* Макроси бітів регістру TIM_BDTR */
#define TIM_BDTR_MOE         (1U << 15) /**< Main output enable */
#define TIM_BDTR_AOE         (1U << 14) /**< Automatic output enable */
#define TIM_BDTR_BKP         (1U << 13) /**< Break polarity */
#define TIM_BDTR_BKE         (1U << 12) /**< Break enable */
#define TIM_BDTR_DTG_MASK    (0xFFU)    /**< Dead-time generator setup mask */

/**
 * @brief Структура конфігурації трифазного ШІМ-драйвера.
 */
typedef struct {
    uint32_t timer_clock_hz; /**< Тактова частота таймера (Гц) */
    uint32_t pwm_freq_hz;    /**< Бажана частота ШІМ (Гц) */
    uint32_t dead_time_ns;   /**< Мертвий час (наносекунди) */
} pwm_config_t;

/**
 * @brief Структура коефіцієнтів заповнення для трьох фаз.
 */
typedef struct {
    float duty_a; /**< Заповнення фази A [0.0 ... 1.0] */
    float duty_b; /**< Заповнення фази B [0.0 ... 1.0] */
    float duty_c; /**< Заповнення фази C [0.0 ... 1.0] */
} pwm_duty_t;

/* Прототипи функцій */
int pwm_driver_init(const pwm_config_t *config);
void pwm_driver_enable_outputs(bool enable);
void pwm_driver_set_duty_cycles(float duty_a, float duty_b, float duty_c);
void pwm_driver_set_raw_ccr(uint16_t ccr_a, uint16_t ccr_b, uint16_t ccr_c);
uint16_t pwm_driver_get_period_ticks(void);
uint8_t pwm_calculate_dtg(uint32_t timer_clk_hz, uint32_t deadtime_ns);
TIM_TypeDef *pwm_driver_get_timer_instance(void);

#endif /* PWM_DRIVER_H */
