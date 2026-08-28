#include <stdint.h>
#include <stdbool.h>

/* Базові адреси шинних контролерів і периферійних модулів */
#define PERIPH_BASE        (0x40000000UL)
#define APB1PERIPH_BASE    (PERIPH_BASE)
#define AHB1PERIPH_BASE    (PERIPH_BASE + 0x00020000UL)

#define RCC_BASE           (AHB1PERIPH_BASE + 0x3800UL)
#define GPIOA_BASE         (AHB1PERIPH_BASE + 0x0000UL)
#define TIM6_BASE          (APB1PERIPH_BASE + 0x1000UL)

/* Структура контролера тактування (RCC) */
typedef struct {
    volatile uint32_t CR;            /* +0x00: Тактування та PLL */
    volatile uint32_t PLLCFGR;       /* +0x04: Конфігурація PLL */
    volatile uint32_t CFGR;          /* +0x08: Дільники шин */
    volatile uint32_t CIR;           /* +0x0C: Переривання тактування */
    volatile uint32_t AHB1RSTR;      /* +0x10: Скидання AHB1 */
    volatile uint32_t AHB2RSTR;      /* +0x14: Скидання AHB2 */
    volatile uint32_t AHB3RSTR;      /* +0x18: Скидання AHB3 */
    uint32_t          RESERVED0;     /* +0x1C: Зарезервовано */
    volatile uint32_t APB1RSTR;      /* +0x20: Скидання APB1 */
    volatile uint32_t APB2RSTR;      /* +0x24: Скидання APB2 */
    uint32_t          RESERVED1[2];  /* +0x28 - +0x2C */
    volatile uint32_t AHB1ENR;       /* +0x30: Увімкнення тактування AHB1 */
    volatile uint32_t AHB2ENR;       /* +0x34: Увімкнення тактування AHB2 */
    volatile uint32_t AHB3ENR;       /* +0x38: Увімкнення тактування AHB3 */
    uint32_t          RESERVED2;     /* +0x3C */
    volatile uint32_t APB1ENR;       /* +0x40: Увімкнення тактування APB1 */
    volatile uint32_t APB2ENR;       /* +0x44: Увімкнення тактування APB2 */
} RCC_TypeDef;

/* Структура модуля GPIO */
typedef struct {
    volatile uint32_t MODER;         /* +0x00: Режим роботи пінів (2 біти на пін) */
    volatile uint32_t OTYPER;        /* +0x04: Тип виходу (Push-Pull / Open-Drain) */
    volatile uint32_t OSPEEDR;       /* +0x08: Швидкість наростання фронту */
    volatile uint32_t PUPDR;         /* +0x0C: Внутрішні підтяжки Pull-Up / Pull-Down */
    volatile uint32_t IDR;           /* +0x10: Регістр вхідних даних (ReadOnly) */
    volatile uint32_t ODR;           /* +0x14: Регістр вихідних даних (ReadWrite) */
    volatile uint32_t BSRR;          /* +0x18: Атомарне встановлення / скидання (WriteOnly) */
    volatile uint32_t LCKR;          /* +0x1C: Блокування конфігурації */
    volatile uint32_t AFR[2];        /* +0x20 - +0x24: Альтернативні функції пінів */
} GPIO_TypeDef;

/* Структура базового таймера (TIM6) */
typedef struct {
    volatile uint32_t CR1;           /* +0x00: Регістр керування 1 (вмикання, автоперезавантаження) */
    volatile uint32_t CR2;           /* +0x04: Регістр керування 2 (тригери) */
    uint32_t          RESERVED0;     /* +0x08 */
    volatile uint32_t DIER;          /* +0x0C: Дозвіл переривань та DMA */
    volatile uint32_t SR;            /* +0x10: Регістр статусу (прапорці оновлення) */
    volatile uint32_t EGR;           /* +0x14: Генерація подій */
    uint32_t          RESERVED1[3];  /* +0x18 - +0x20 */
    volatile uint32_t CNT;           /* +0x24: Лічильник поточного значення */
    volatile uint32_t PSC;           /* +0x28: Дільник частоти (Prescaler) */
    volatile uint32_t ARR;           /* +0x2C: Межа автоперезавантаження */
} TIM_TypeDef;

#define RCC    ((RCC_TypeDef *)RCC_BASE)
#define GPIOA  ((GPIO_TypeDef *)GPIOA_BASE)
#define TIM6   ((TIM_TypeDef *)TIM6_BASE)
