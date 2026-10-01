#ifndef DAPLINK_BOARD_H
#define DAPLINK_BOARD_H

#include <stdint.h>
#include <stdbool.h>

// Макроси бітових операцій та регістрів STM32F103
#define PERIPH_BASE           (0x40000000UL)
#define APB2PERIPH_BASE       (PERIPH_BASE + 0x10000UL)
#define AHBPERIPH_BASE        (PERIPH_BASE + 0x20000UL)

#define RCC_BASE              (AHBPERIPH_BASE + 0x1000UL)
#define GPIOA_BASE            (APB2PERIPH_BASE + 0x0800UL)
#define GPIOB_BASE            (APB2PERIPH_BASE + 0x0C00UL)

// Структура регістрів GPIO STM32F103
typedef struct {
    volatile uint32_t CRL;
    volatile uint32_t CRH;
    volatile uint32_t IDR;
    volatile uint32_t ODR;
    volatile uint32_t BSRR;
    volatile uint32_t BRR;
    volatile uint32_t LCKR;
} GPIO_TypeDef;

// Структура регістрів RCC STM32F103
typedef struct {
    volatile uint32_t CR;
    volatile uint32_t CFGR;
    volatile uint32_t CIR;
    volatile uint32_t APB2RSTR;
    volatile uint32_t APB1RSTR;
    volatile uint32_t AHBENR;
    volatile uint32_t APB2ENR;
    volatile uint32_t APB1ENR;
    volatile uint32_t BDCR;
    volatile uint32_t CSR;
} RCC_TypeDef;

#define GPIOA                 ((GPIO_TypeDef *) GPIOA_BASE)
#define GPIOB                 ((GPIO_TypeDef *) GPIOB_BASE)
#define RCC                   ((RCC_TypeDef *) RCC_BASE)

// Розпинівка адаптера DAPLink на STM32F103 (Port A)
// SWCLK: PA5, Output Push-Pull 50MHz
// SWDIO: PA6, Bidirectional Open-Drain / Push-Pull 50MHz
// nRESET: PA7, Output Open-Drain (Active LOW)
#define PIN_SWCLK             (5U)
#define PIN_SWDIO             (6U)
#define PIN_NRESET            (7U)

// Швидкісні макроси встановлення/скидання ліній через регістри BSRR та BRR
#define SWCLK_HIGH()          (GPIOA->BSRR = (1U << PIN_SWCLK))
#define SWCLK_LOW()           (GPIOA->BRR  = (1U << PIN_SWCLK))

#define SWDIO_HIGH()          (GPIOA->BSRR = (1U << PIN_SWDIO))
#define SWDIO_LOW()           (GPIOA->BRR  = (1U << PIN_SWDIO))
#define SWDIO_READ()          ((GPIOA->IDR >> PIN_SWDIO) & 0x01U)

#define NRESET_HIGH()         (GPIOA->BSRR = (1U << PIN_NRESET))
#define NRESET_LOW()          (GPIOA->BRR  = (1U << PIN_NRESET))

// Режими роботи виводу SWDIO
typedef enum {
    SWDIO_MODE_OUTPUT_PP = 0, // Вихід Push-Pull для передачі даних
    SWDIO_MODE_INPUT_PULLUP   // Вхід Pull-Up для зчитання відповіді цілі (ACK/Data)
} SWDIO_Mode_t;

// Структура конфігурації портів DAPLink
typedef struct {
    uint32_t clock_speed_hz;  // Поточна частота SWCLK у Гц
    SWDIO_Mode_t swdio_mode;  // Поточний режим лінії SWDIO
    bool reset_active;        // Прапорець активного стану лінії nRESET
} DAP_PortConfig_t;

// Зовнішня змінна конфігурації порту
extern DAP_PortConfig_t g_dap_port_config;

#endif // DAPLINK_BOARD_H
