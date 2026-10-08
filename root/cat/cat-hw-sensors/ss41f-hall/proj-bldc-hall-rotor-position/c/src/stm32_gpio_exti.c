#include "stm32_gpio_exti.h"
#include <stddef.h>

/**
 * @brief CMSIS-сумісні структури регістрів STM32 для роботи з периферією.
 */
typedef struct {
    volatile uint32_t MODER;   /**< Регістр режиму роботи пінів */
    volatile uint32_t OTYPER;  /**< Регістр типу виходу */
    volatile uint32_t OSPEEDR; /**< Регістр швидкості */
    volatile uint32_t PUPDR;   /**< Регістр підтяжки Pull-up / Pull-down */
    volatile uint32_t IDR;     /**< Регістр вхідних даних */
    volatile uint32_t ODR;     /**< Регістр вихідних даних */
} GPIO_TypeDef;

typedef struct {
    volatile uint32_t IMR;     /**< Маска переривань */
    volatile uint32_t EMR;     /**< Маска подій */
    volatile uint32_t RTSR;    /**< Тригер наростаючого фронту (Rising) */
    volatile uint32_t FTSR;    /**< Тригер спадаючого фронту (Falling) */
    volatile uint32_t SWIER;   /**< Програмне переривання */
    volatile uint32_t PR;      /**< Регістр прапорців очікування (Pending) */
} EXTI_TypeDef;

typedef struct {
    volatile uint32_t MEMRMP;
    volatile uint32_t PMC;
    volatile uint32_t EXTICR[4]; /**< Конфігурація ліній EXTI до портів GPIO */
} SYSCFG_TypeDef;

/* Структури регістрів периферії для STM32 */
static GPIO_TypeDef   mock_gpiob;
static EXTI_TypeDef   mock_exti;
static SYSCFG_TypeDef mock_syscfg;

#ifndef HALL_GPIO_PORT
#define HALL_GPIO_PORT (&mock_gpiob)
#endif

#ifndef EXTI
#define EXTI           (&mock_exti)
#endif

#ifndef SYSCFG
#define SYSCFG         (&mock_syscfg)
#endif

static stm32_exti_isr_callback_t g_exti_callback = NULL;

void stm32_gpio_exti_init(void) {
    /* 1. Налаштування GPIO (PB0, PB1, PB2 як входи з підтяжкою Pull-up для SS41F) */
    HALL_GPIO_PORT->MODER &= ~((0x03U << (HALL_PIN_A_BIT * 2)) |
                               (0x03U << (HALL_PIN_B_BIT * 2)) |
                               (0x03U << (HALL_PIN_C_BIT * 2)));

    /* Режим Pull-up (01), бо SS41F має вихід з відкритим колектором */
    HALL_GPIO_PORT->PUPDR &= ~((0x03U << (HALL_PIN_A_BIT * 2)) |
                               (0x03U << (HALL_PIN_B_BIT * 2)) |
                               (0x03U << (HALL_PIN_C_BIT * 2)));
    HALL_GPIO_PORT->PUPDR |=  ((0x01U << (HALL_PIN_A_BIT * 2)) |
                               (0x01U << (HALL_PIN_B_BIT * 2)) |
                               (0x01U << (HALL_PIN_C_BIT * 2)));

    /* 2. Прив'язка ліній EXTI0, EXTI1, EXTI2 до порту GPIOB в SYSCFG_EXTICR1 */
    SYSCFG->EXTICR[0] &= ~(0x0FFF);
    SYSCFG->EXTICR[0] |=  (0x0111);

    /* 3. Конфігурація тригерів обох фронтів (Rising та Falling edge) в EXTI */
    EXTI->IMR  |= HALL_PINS_ALL_MASK;  /* Увімкнення переривань для ліній 0, 1, 2 */
    EXTI->RTSR |= HALL_PINS_ALL_MASK; /* Детектування наростаючого фронту */
    EXTI->FTSR |= HALL_PINS_ALL_MASK; /* Детектування спадаючого фронту */
}

uint8_t stm32_gpio_read_hall_pins(void) {
    uint32_t idr = HALL_GPIO_PORT->IDR;
    return (uint8_t)STM32_READ_HALL_RAW_CODE(idr);
}

void stm32_exti_register_callback(stm32_exti_isr_callback_t cb) {
    g_exti_callback = cb;
}

/**
 * @brief Узагальнений внутрішній обробник переривання EXTI для ліній давачів.
 */
static inline void handle_exti_hall_interrupt(uint32_t pin_mask) {
    if ((EXTI->PR & pin_mask) != 0U) {
        /* Скидання прапорця переривання в регістрі PR */
        EXTI->PR = pin_mask;

        /* Атомарне зчитування 3-бітового коду з IDR */
        uint8_t raw_code = stm32_gpio_read_hall_pins();

        /* Передача стану до шару обробки без затримок у контексті ISR */
        if (g_exti_callback != NULL) {
            g_exti_callback(raw_code);
        }
    }
}

/**
 * @brief Апаратний ISR для EXTI Line 0 (Hall A / PB0).
 */
void EXTI0_IRQHandler(void) {
    handle_exti_hall_interrupt(HALL_PIN_A_MASK);
}

/**
 * @brief Апаратний ISR для EXTI Line 1 (Hall B / PB1).
 */
void EXTI1_IRQHandler(void) {
    handle_exti_hall_interrupt(HALL_PIN_B_MASK);
}

/**
 * @brief Апаратний ISR для EXTI Line 2 (Hall C / PB2).
 */
void EXTI2_IRQHandler(void) {
    handle_exti_hall_interrupt(HALL_PIN_C_MASK);
}
