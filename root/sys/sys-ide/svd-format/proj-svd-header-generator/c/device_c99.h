/* Згенерований файл device_c99.h */
#ifndef __MICRO32_CMSIS_H__
#define __MICRO32_CMSIS_H__

#include <stdint.h>
#include <stddef.h>

#define __I     volatile const
#define __O     volatile
#define __IO    volatile

typedef enum {
    NonMaskableInt_IRQn   = -14,
    HardFault_IRQn        = -13,
    MemoryManagement_IRQn = -12,
    BusFault_IRQn         = -11,
    UsageFault_IRQn       = -10,
    SVCall_IRQn           = -5,
    PendSV_IRQn           = -2,
    SysTick_IRQn          = -1,
    USART1_IRQn           = 37,
    USART2_IRQn           = 38,
} IRQn_Type;

typedef struct {
    __IO uint32_t SR;               /*!< Зсув 0x0000: Status register */
    __IO uint32_t DR;               /*!< Зсув 0x0004: Data register */
    uint8_t  RESERVED_0[4];         /*!< Зсув 0x0008..0x000B (автоматичний розрахунок прогалини) */
    __IO uint32_t CR1;              /*!< Зсув 0x000C: Control register 1 */
} USART_TypeDef;

/* Статична валідація зміщень полів на етапі компіляції */
_Static_assert(offsetof(USART_TypeDef, SR)  == 0x00, "Помилка зміщення USART_TypeDef->SR");
_Static_assert(offsetof(USART_TypeDef, DR)  == 0x04, "Помилка зміщення USART_TypeDef->DR");
_Static_assert(offsetof(USART_TypeDef, CR1) == 0x0C, "Помилка зміщення USART_TypeDef->CR1");
_Static_assert(sizeof(USART_TypeDef)        == 0x10, "Помилка загального розміру USART_TypeDef");

/* Бітові маски та зміщення полів */
#define USART_SR_RXNE_Pos       (5U)
#define USART_SR_RXNE_Msk       (0x1U << USART_SR_RXNE_Pos)
#define USART_SR_RXNE           USART_SR_RXNE_Msk

#define USART_CR1_UE_Pos        (0U)
#define USART_CR1_UE_Msk        (0x1U << USART_CR1_UE_Pos)
#define USART_CR1_UE            USART_CR1_UE_Msk

#define USART_CR1_M_Pos         (12U)
#define USART_CR1_M_Msk         (0x1U << USART_CR1_M_Pos)
#define USART_CR1_M             USART_CR1_M_Msk
#define USART_CR1_M_M_8BIT      (0x0U << USART_CR1_M_Pos)
#define USART_CR1_M_M_9BIT      (0x1U << USART_CR1_M_Pos)

/* Базові адреси та покажчики на структури периферії */
#define USART1_BASE             (0x40013800UL)
#define USART1                  ((USART_TypeDef *) USART1_BASE)

#define USART2_BASE             (0x40004400UL)
#define USART2                  ((USART_TypeDef *) USART2_BASE)

#endif /* __MICRO32_CMSIS_H__ */
