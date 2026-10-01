#include "target.h"

/* Регістри мікроконтролера STM32F103C8T6 (CMSIS / Базові адреси периферії) */
#define RCC_BASE            0x40021000U
#define GPIOA_BASE          0x40010800U
#define GPIOB_BASE          0x40010C00U
#define GPIOC_BASE          0x40011000U
#define USART1_BASE         0x40013800U

/* Зсуви регістрів RCC */
#define RCC_CR              (*(volatile uint32_t *)(RCC_BASE + 0x00U))
#define RCC_CFGR            (*(volatile uint32_t *)(RCC_BASE + 0x04U))
#define RCC_APB2ENR         (*(volatile uint32_t *)(RCC_BASE + 0x18U))

/* Зсуви регістрів GPIO */
#define GPIOA_CRL           (*(volatile uint32_t *)(GPIOA_BASE + 0x00U))
#define GPIOA_CRH           (*(volatile uint32_t *)(GPIOA_BASE + 0x04U))
#define GPIOA_IDR           (*(volatile uint32_t *)(GPIOA_BASE + 0x08U))
#define GPIOA_ODR           (*(volatile uint32_t *)(GPIOA_BASE + 0x0CU))
#define GPIOA_BSRR          (*(volatile uint32_t *)(GPIOA_BASE + 0x10U))
#define GPIOA_BRR           (*(volatile uint32_t *)(GPIOA_BASE + 0x14U))

#define GPIOB_CRL           (*(volatile uint32_t *)(GPIOB_BASE + 0x00U))
#define GPIOB_ODR           (*(volatile uint32_t *)(GPIOB_BASE + 0x0CU))
#define GPIOB_BSRR          (*(volatile uint32_t *)(GPIOB_BASE + 0x10U))
#define GPIOB_BRR           (*(volatile uint32_t *)(GPIOB_BASE + 0x14U))

#define GPIOC_CRH           (*(volatile uint32_t *)(GPIOC_BASE + 0x04U))
#define GPIOC_BSRR          (*(volatile uint32_t *)(GPIOC_BASE + 0x10U))
#define GPIOC_BRR           (*(volatile uint32_t *)(GPIOC_BASE + 0x14U))

/* Зсуви регістрів USART1 */
#define USART1_SR           (*(volatile uint32_t *)(USART1_BASE + 0x00U))
#define USART1_DR           (*(volatile uint32_t *)(USART1_BASE + 0x04U))
#define USART1_BRR          (*(volatile uint32_t *)(USART1_BASE + 0x08U))
#define USART1_CR1          (*(volatile uint32_t *)(USART1_BASE + 0x0CU))

/* Біти системного тактування RCC */
#define RCC_APB2ENR_IOPAEN  (1U << 2)
#define RCC_APB2ENR_IOPBEN  (1U << 3)
#define RCC_APB2ENR_IOPCEN  (1U << 4)
#define RCC_APB2ENR_USART1EN (1U << 14)

/**
 * @brief Ініціалізація системного тактування RCC (72 МГц від HSE 8 МГц через PLL)
 */
static void rcc_init(void)
{
    /* Увімкнення зовнішнього кварцового резонатора HSE (8 МГц) */
    RCC_CR |= (1U << 16);
    while (!(RCC_CR & (1U << 17))) {
        /* Очікування готовності HSE */
    }

    /* Налаштування Flash Latency = 2 та дельфіна PLL = 9 (8 МГц * 9 = 72 МГц) */
    *(volatile uint32_t *)0x40022000U = 0x12U; /* FLASH_ACR: 2 cycles latency */

    /* CFGR: PLLSRC = HSE, PLLMUL = 9, PPRE1 = 2 (APB1 = 36 МГц) */
    RCC_CFGR &= ~((0x0FU << 18) | (1U << 16) | (0x07U << 8));
    RCC_CFGR |= ((0x07U << 18) | (1U << 16) | (0x04U << 8));

    /* Увімкнення генератора PLL */
    RCC_CR |= (1U << 24);
    while (!(RCC_CR & (1U << 25))) {
        /* Очікування захоплення частоти PLL */
    }

    /* Перемикання системного тактування SYSCLK на джерело PLL */
    RCC_CFGR &= ~(0x03U);
    RCC_CFGR |= 0x02U;
    while ((RCC_CFGR & (0x0CU)) != 0x08U) {
        /* Очікування перемикання на PLL */
    }

    /* Вмикання тактування портів GPIOA, GPIOB, GPIOC та USART1 */
    RCC_APB2ENR |= RCC_APB2ENR_IOPAEN | RCC_APB2ENR_IOPBEN |
                   RCC_APB2ENR_IOPCEN | RCC_APB2ENR_USART1EN;
}

/**
 * @brief Початкова конфігурація периферійних виводів GPIO для інтерфейсів DAPLink
 */
void target_init(void)
{
    rcc_init();

    /* 1. Конфігурація PA5 (SWCLK) як Output Push-Pull 50MHz (MODE=11, CNF=00 -> 0x3) */
    GPIOA_CRL &= ~(0x0FU << (5 * 4));
    GPIOA_CRL |=  (0x03U << (5 * 4));

    /* 2. Конфігурація PA6 (SWDIO) за замовчуванням як Output Open-Drain 50MHz (MODE=11, CNF=01 -> 0x7) */
    target_swdio_set_output();

    /* 3. Конфігурація PB0 (nRESET) як Output Open-Drain 50MHz (MODE=11, CNF=01 -> 0x7) */
    GPIOB_CRL &= ~(0x0FU << (0 * 4));
    GPIOB_CRL |=  (0x07U << (0 * 4));
    target_reset_deassert();

    /* 4. Конфігурація PB1 (TARGET_PWR) як Output Push-Pull 50MHz (MODE=11, CNF=00 -> 0x3) */
    GPIOB_CRL &= ~(0x0FU << (1 * 4));
    GPIOB_CRL |=  (0x03U << (1 * 4));
    target_power_on();

    /* 5. Конфігурація PC13, PC14, PC15 (LEDs) як Output Push-Pull 2MHz (MODE=10, CNF=00 -> 0x2) */
    GPIOC_CRH &= ~((0x0FU << (5 * 4)) | (0x0FU << (6 * 4)) | (0x0FU << (7 * 4)));
    GPIOC_CRH |=  ((0x02U << (5 * 4)) | (0x02U << (6 * 4)) | (0x02U << (7 * 4)));

    /* Вимкнення світлодіодів при старті (виводи PC13-PC15 у HIGH для активного LOW) */
    GPIOC_BSRR = LED_CONNECTED_PIN | LED_RUNNING_PIN | LED_ACTIVITY_PIN;
}

/**
 * @brief Подача живлення на цільову плату (Target VCC ON)
 */
void target_power_on(void)
{
    GPIOB_BSRR = TARGET_PWR_PIN; /* Установлення PB1 у HIGH */
}

/**
 * @brief Відключення живлення цільової плати (Target VCC OFF)
 */
void target_power_off(void)
{
    GPIOB_BRR = TARGET_PWR_PIN;  /* Скидання PB1 у LOW */
}

/**
 * @brief Примусове утримання цільового МК у стані скидання (nRESET = LOW)
 */
void target_reset_assert(void)
{
    GPIOB_BRR = TARGET_RESET_PIN; /* Притягування PB0 до GND */
}

/**
 * @brief Зняття сигналу скидання (nRESET High-Z / Pull-Up)
 */
void target_reset_deassert(void)
{
    GPIOB_BSRR = TARGET_RESET_PIN; /* Відпускання PB0 у VCC */
}

/**
 * @brief Переведення лінії SWDIO у режим входу (Input Floating) для прийому даних
 */
void target_swdio_set_input(void)
{
    GPIOA_CRL &= ~(0x0FU << (6 * 4));
    GPIOA_CRL |=  (0x04U << (6 * 4)); /* MODE=00, CNF=01 (Input Floating) */
}

/**
 * @brief Переведення лінії SWDIO у режим виходу (Output Open-Drain 50MHz)
 */
void target_swdio_set_output(void)
{
    GPIOA_CRL &= ~(0x0FU << (6 * 4));
    GPIOA_CRL |=  (0x07U << (6 * 4)); /* MODE=11, CNF=01 (Output Open-Drain) */
}

/**
 * @brief Керування світлодіодними індикаторами стану DAPLink
 * @param led Тип світлодіода (LED_CONNECTED, LED_RUNNING, LED_ACTIVITY)
 * @param state true — увімкнути, false — вимкнути
 */
void target_set_led(daplink_led_t led, bool state)
{
    uint32_t pin = 0;
    switch (led) {
        case LED_CONNECTED:
            pin = LED_CONNECTED_PIN;
            break;
        case LED_RUNNING:
            pin = LED_RUNNING_PIN;
            break;
        case LED_ACTIVITY:
            pin = LED_ACTIVITY_PIN;
            break;
        default:
            return;
    }

    /* Індикатори підключені за схемою Active Low */
    if (state) {
        GPIOC_BRR = pin;  /* LOW = LED ON */
    } else {
        GPIOC_BSRR = pin; /* HIGH = LED OFF */
    }
}

/**
 * @brief Налаштування модуля USART1 для підтримки віртуального COM-порту (CDC UART)
 * @param baudrate Необхідна швидкість передачі в бодах (наприклад, 115200)
 */
void target_usart1_init(uint32_t baudrate)
{
    /* Налаштування PA9 (TX) як Alternate Function Push-Pull (MODE=11, CNF=10 -> 0xB) */
    GPIOA_CRH &= ~(0x0FU << (1 * 4));
    GPIOA_CRH |=  (0x0BU << (1 * 4));

    /* Налаштування PA10 (RX) як Input Floating (MODE=00, CNF=01 -> 0x4) */
    GPIOA_CRH &= ~(0x0FU << (2 * 4));
    GPIOA_CRH |=  (0x04U << (2 * 4));

    /* Обчислення дільника швидкості USART1 при PCLK2 = 72 МГц */
    uint32_t usartdiv = (72000000U + (baudrate / 2U)) / baudrate;
    USART1_BRR = usartdiv;

    /* Вмикання передавача (TE), приймача (RE) та самого модуля USART1 (UE) */
    USART1_CR1 = (1U << 13) | (1U << 3) | (1U << 2);
}
