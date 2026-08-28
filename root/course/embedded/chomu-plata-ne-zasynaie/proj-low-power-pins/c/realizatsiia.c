#include <stdint.h>
#include <stdbool.h>

/* Базові адреси регістрів STM32 (регістровий рівень) */
#define DBGMCU_BASE_ADDR   0xE0042000UL
#define DBGMCU_CR_REG      (*(volatile uint32_t *)(DBGMCU_BASE_ADDR + 0x04UL))

#define GPIOA_BASE_ADDR    0x48000000UL
#define GPIOB_BASE_ADDR    0x48000400UL
#define GPIOC_BASE_ADDR    0x48000800UL

typedef struct {
    volatile uint32_t MODER;    /* Режим виводу: 00-Input, 01-Output, 10-AF, 11-Analog */
    volatile uint32_t OTYPER;   /* Тип виходу: 0-Push-Pull, 1-Open-Drain */
    volatile uint32_t OSPEEDR;  /* Швидкість перемикання */
    volatile uint32_t PUPDR;    /* Підтяжки: 00-Floating, 01-Pull-up, 10-Pull-down */
    volatile uint32_t IDR;      /* Вхідні дані */
    volatile uint32_t ODR;      /* Вихідні дані */
    volatile uint32_t BSRR;     /* Встановлення/скидання бітів */
    volatile uint32_t LCKR;     /* Блокування конфігурації */
    volatile uint32_t AFR[2];   /* Альтернативні функції */
    volatile uint32_t BRR;      /* Скидання бітів виходу */
} LowPower_GPIO_TypeDef;

#define LP_GPIOA ((LowPower_GPIO_TypeDef *)GPIOA_BASE_ADDR)
#define LP_GPIOB ((LowPower_GPIO_TypeDef *)GPIOB_BASE_ADDR)
#define LP_GPIOC ((LowPower_GPIO_TypeDef *)GPIOC_BASE_ADDR)

/* Маски збережених пінів (наприклад, пін пробудження PA0 та пін ключа живлення PB12) */
#define PIN_WAKEUP_PA0       (1U << 0)
#define PIN_LOAD_SWITCH_PB12 (1U << 12)

typedef struct {
    uint32_t moder_a;
    uint32_t pupdr_a;
    uint32_t moder_b;
    uint32_t pupdr_b;
    uint32_t moder_c;
    uint32_t pupdr_c;
} GpioBackupContext;

static GpioBackupContext g_gpio_backup;

/**
 * @brief Вимкнення силового ключа периферії
 */
void power_switch_set(bool enable)
{
    if (enable) {
        /* P-MOSFET відкривається нулем (активний LOW) */
        LP_GPIOB->BSRR = (PIN_LOAD_SWITCH_PB12 << 16U);
    } else {
        /* P-MOSFET закривається одиницею */
        LP_GPIOB->BSRR = PIN_LOAD_SWITCH_PB12;
    }
}

/**
 * @brief Підготовка всіх виводів до сну: переведення в Analog mode
 */
void low_power_pins_enter_sleep(void)
{
    /* 1. Збереження поточної конфігурації для відновлення після сну */
    g_gpio_backup.moder_a = LP_GPIOA->MODER;
    g_gpio_backup.pupdr_a = LP_GPIOA->PUPDR;
    g_gpio_backup.moder_b = LP_GPIOB->MODER;
    g_gpio_backup.pupdr_b = LP_GPIOB->PUPDR;
    g_gpio_backup.moder_c = LP_GPIOC->MODER;
    g_gpio_backup.pupdr_c = LP_GPIOC->PUPDR;

    /* 2. Ізоляція сигнальних ліній периферії (зведення в LOW) */
    LP_GPIOA->ODR &= ~((1U << 2) | (1U << 3) | (1U << 5) | (1U << 7)); /* UART TX/RX, SPI MOSI/SCK */

    /* 3. Знеструмлення зовнішніх датчиків */
    power_switch_set(false);

    /* 4. Переведення виводів у режим Analog (MODER = 0xFFFFFFFF, PUPDR = 0x00000000)
          Виняток: пін пробудження PA0 та пін силового ключа PB12 залишаються у визначеному стані */
    
    /* Порт A: всі в Analog, крім PA0 (Wakeup) */
    LP_GPIOA->MODER = 0xFFFFFFFCUL | (g_gpio_backup.moder_a & 0x03UL);
    LP_GPIOA->PUPDR = 0x00000000UL | (g_gpio_backup.pupdr_a & 0x03UL);

    /* Порт B: всі в Analog, крім PB12 (Load Switch Output High) */
    uint32_t pb12_moder_mask = (3U << (12 * 2));
    LP_GPIOB->MODER = (~pb12_moder_mask) | (g_gpio_backup.moder_b & pb12_moder_mask);
    LP_GPIOB->PUPDR = 0x00000000UL;

    /* Порт C: всі виводи в чистий Analog */
    LP_GPIOC->MODER = 0xFFFFFFFFUL;
    LP_GPIOC->PUPDR = 0x00000000UL;

    /* 5. Вимкнення тактування блоку налагодження під час зупинки ядра */
    DBGMCU_CR_REG = 0x00000000UL;
}

/**
 * @brief Відновлення конфігурації виводів після виходу зі сну
 */
void low_power_pins_restore(void)
{
    /* Відновлення конфігурації портів з резервної копії */
    LP_GPIOA->MODER = g_gpio_backup.moder_a;
    LP_GPIOA->PUPDR = g_gpio_backup.pupdr_a;

    LP_GPIOB->MODER = g_gpio_backup.moder_b;
    LP_GPIOB->PUPDR = g_gpio_backup.pupdr_b;

    LP_GPIOC->MODER = g_gpio_backup.moder_c;
    LP_GPIOC->PUPDR = g_gpio_backup.pupdr_c;

    /* Повторне ввімкнення живлення периферії */
    power_switch_set(true);
}
