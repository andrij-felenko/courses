#ifndef STM32_TIMER_HAL_H
#define STM32_TIMER_HAL_H

#include <stdint.h>
#include <stdbool.h>

/**
 * @brief Структура регістрів таймера STM32 (згідно з CMSIS / Reference Manual RM0008/RM0090)
 */
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
} TIM_TypeDef;

/**
 * @brief Структура регістрів EXTI (External Interrupt Controller)
 */
typedef struct {
    volatile uint32_t IMR;   /**< Interrupt mask register */
    volatile uint32_t EMR;   /**< Event mask register */
    volatile uint32_t RTSR;  /**< Rising trigger selection register */
    volatile uint32_t FTSR;  /**< Falling trigger selection register */
    volatile uint32_t SWIER; /**< Software interrupt event register */
    volatile uint32_t PR;    /**< Pending register */
} EXTI_TypeDef;

/* Бітові маски регістра CR1 */
#define TIM_CR1_CEN_Pos          (0U)
#define TIM_CR1_CEN              (1U << TIM_CR1_CEN_Pos)       /**< Увімкнення лічильника */
#define TIM_CR1_DIR_Pos          (4U)
#define TIM_CR1_DIR              (1U << TIM_CR1_DIR_Pos)       /**< Напрямок підрахунку: 0 = Up, 1 = Down */

/* Бітові маски регістра SMCR */
#define TIM_SMCR_SMS_Pos         (0U)
#define TIM_SMCR_SMS_Msk         (0x7U << TIM_SMCR_SMS_Pos)
#define TIM_SMCR_SMS_ENCODER3    (0x3U << TIM_SMCR_SMS_Pos)    /**< Режим квадратурного енкодера Mode 3 (x4) */

/* Бітові маски регістра CCMR1 */
#define TIM_CCMR1_CC1S_Pos       (0U)
#define TIM_CCMR1_CC1S_Msk       (0x3U << TIM_CCMR1_CC1S_Pos)
#define TIM_CCMR1_CC1S_INPUT_TI1 (0x1U << TIM_CCMR1_CC1S_Pos)   /**< Канал IC1 підключено до TI1 (Phase A) */

#define TIM_CCMR1_IC1F_Pos       (4U)
#define TIM_CCMR1_IC1F_Msk       (0xFU << TIM_CCMR1_IC1F_Pos)  /**< Цифровий фільтр входу IC1 (ICF) */

#define TIM_CCMR1_CC2S_Pos       (8U)
#define TIM_CCMR1_CC2S_Msk       (0x3U << TIM_CCMR1_CC2S_Pos)
#define TIM_CCMR1_CC2S_INPUT_TI2 (0x1U << TIM_CCMR1_CC2S_Pos)   /**< Канал IC2 підключено до TI2 (Phase B) */

#define TIM_CCMR1_IC2F_Pos       (12U)
#define TIM_CCMR1_IC2F_Msk       (0xFU << TIM_CCMR1_IC2F_Pos)  /**< Цифровий фільтр входу IC2 (ICF) */

/* Бітові маски регістра CCER */
#define TIM_CCER_CC1P_Pos        (1U)
#define TIM_CCER_CC1P            (1U << TIM_CCER_CC1P_Pos)     /**< Полярність IC1 */
#define TIM_CCER_CC2P_Pos        (5U)
#define TIM_CCER_CC2P            (1U << TIM_CCER_CC2P_Pos)     /**< Полярність IC2 */

/* Бітові маски регістрів DIER та SR */
#define TIM_DIER_UIE_Pos         (0U)
#define TIM_DIER_UIE             (1U << TIM_DIER_UIE_Pos)      /**< Дозвіл переривання оновлення (Update Interrupt) */

#define TIM_SR_UIF_Pos           (0U)
#define TIM_SR_UIF               (1U << TIM_SR_UIF_Pos)        /**< Прапорець переривання оновлення */

/**
 * @brief Полярність вхідних сигналів енкодера
 */
typedef enum {
    TIM_ENCODER_POLARITY_RISING = 0,  /**< Пряма полярність (сигнал без інверсії) */
    TIM_ENCODER_POLARITY_FALLING = 1  /**< Інвертована полярність */
} timer_encoder_polarity_t;

/**
 * @brief Значення вхідного цифрового фільтра (ICF: Input Capture Filter)
 * Визначає кількість послідовних тактів f_DTS, протягом яких рівень має бути стабільним.
 */
typedef enum {
    TIM_IC_FILTER_NONE          = 0x0, /**< Без фільтрації (пряме підключення) */
    TIM_IC_FILTER_FDTS_N2       = 0x1, /**< Фільтр f_SAMPLING = f_DTS, N=2 */
    TIM_IC_FILTER_FDTS_N4       = 0x2, /**< Фільтр f_SAMPLING = f_DTS, N=4 */
    TIM_IC_FILTER_FDTS_N8       = 0x3, /**< Фільтр f_SAMPLING = f_DTS, N=8 (оптимально) */
    TIM_IC_FILTER_FDTS_DIV4_N6  = 0x6, /**< Фільтр f_SAMPLING = f_DTS/4, N=6 */
    TIM_IC_FILTER_FDTS_DIV16_N8 = 0xD, /**< Фільтр f_SAMPLING = f_DTS/16, N=8 */
    TIM_IC_FILTER_FDTS_DIV32_N8 = 0xF  /**< Фільтр f_SAMPLING = f_DTS/32, N=8 (максимальне приглушення) */
} timer_ic_filter_t;

/**
 * @brief Структура конфігурації апаратного таймера STM32
 */
typedef struct {
    TIM_TypeDef *timer;                    /**< Вказівник на перифірійний таймер (TIM2, TIM3, TIM4 тощо) */
    timer_ic_filter_t filter_ch1;          /**< Налаштування цифрового фільтра входу CH1 (Phase A) */
    timer_ic_filter_t filter_ch2;          /**< Налаштування цифрового фільтра входу CH2 (Phase B) */
    timer_encoder_polarity_t polarity_ch1; /**< Полярність входу CH1 */
    timer_encoder_polarity_t polarity_ch2; /**< Полярність входу CH2 */
    uint16_t auto_reload;                  /**< Значення автоперезавантаження ARR (0xFFFF для 16 біт) */
    uint32_t exti_line;                    /**< Лінія EXTI для індексного сигналу Z (наприклад, 1U << 0) */
} stm32_timer_config_t;

/**
 * @brief Ініціалізація перифірійного таймера у режимі квадратурного декодера (Encoder Mode 3 — x4)
 * @param config Конфігураційні параметри
 * @return true у разі успішної ініціалізації
 */
bool stm32_timer_encoder_init(const stm32_timer_config_t *config);

/**
 * @brief Ініціалізація зовнішнього переривання EXTI для обробки індексного імпульсу Z
 * @param config Конфігураційні параметри
 * @return true у разі успішної конфігурації
 */
bool stm32_timer_exti_z_init(const stm32_timer_config_t *config);

/**
 * @brief Отримання поточного значення лічильника CNT таймера
 * @param timer Вказівник на таймер
 * @return 16-бітне значення лічильника CNT
 */
static inline uint16_t stm32_timer_get_counter(const TIM_TypeDef *timer) {
    return (uint16_t)(timer->CNT & 0xFFFFU);
}

/**
 * @brief Зчитування поточного напрямку підрахунку з регістра CR1
 * @param timer Вказівник на таймер
 * @return true якщо підрахунок іде у зворотному напрямку (downcounting), false якщо у прямому (upcounting)
 */
static inline bool stm32_timer_get_direction_down(const TIM_TypeDef *timer) {
    return (timer->CR1 & TIM_CR1_DIR) != 0U;
}

/**
 * @brief Перевірка та очищення прапорця переповнення Update Interrupt (UIF)
 * @param timer Вказівник на таймер
 * @return true якщо прапорець UIF було встановлено
 */
bool stm32_timer_check_and_clear_update_flag(TIM_TypeDef *timer);

#endif /* STM32_TIMER_HAL_H */
