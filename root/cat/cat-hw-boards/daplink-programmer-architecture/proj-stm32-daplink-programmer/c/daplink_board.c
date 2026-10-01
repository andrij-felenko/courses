#include "target_board.h"

/*
 * Драйверний модуль шару плати (Board Layer) прошивки DAPLink.
 * Реалізує низькорівневу ініціалізацію тактування GPIO, конфігурацію напрямку
 * лінії SWDIO, налаштування буферів та сигналів системного скидання nRESET.
 */

// Макетні структури регістрів GPIO (спрощена модель CMSIS для навчального прикладу)
typedef struct {
    volatile uint32_t CRL;
    volatile uint32_t CRH;
    volatile uint32_t IDR;
    volatile uint32_t ODR;
    volatile uint32_t BSRR;
    volatile uint32_t BRR;
} GPIO_TypeDef;

#define GPIOA_BASE 0x40010800U
#define GPIOB_BASE 0x40010C00U
#define GPIOA ((GPIO_TypeDef *) GPIOA_BASE)
#define GPIOB ((GPIO_TypeDef *) GPIOB_BASE)

// Ініціалізація периферійних портів плати програматора
void board_init(void) {
    // Конфігурація SWCLK (PA5) як вихід Push-Pull 50 МГц
    GPIOA->CRL &= ~(0x0F << (5 * 4));
    GPIOA->CRL |=  (0x03 << (5 * 4));

    // Початкова конфігурація SWDIO (PA6) як вихід з підтяжкою
    board_set_swd_dir(true);

    // Конфігурація nRESET (PB0) як вихід Open-Drain із затисканням
    GPIOB->CRL &= ~(0x0F << (0 * 4));
    GPIOB->CRL |=  (0x07 << (0 * 4)); // Open-Drain 10 МГц
    PIN_RESET_DEASSERT();             // Пасивний стан (HIGH)

    // Конфігурація світлодіодів PB12, PB13 як виходи Push-Pull
    GPIOB->CRH &= ~((0x0F << (4 * 4)) | (0x0F << (5 * 4)));
    GPIOB->CRH |=  ((0x03 << (4 * 4)) | (0x03 << (5 * 4)));
    
    board_set_led_state(LED_CONNECTED_PIN, false);
    board_set_led_state(LED_RUNNING_PIN, false);
}

// Динамічне перемикання напрямку лінії SWDIO (вхід/вихід) під час SWD-транзакцій
void board_set_swd_dir(bool output) {
    GPIOA->CRL &= ~(0x0F << (6 * 4));
    if (output) {
        // Вихід Push-Pull 50 МГц для відправки команд від програматора
        GPIOA->CRL |= (0x03 << (6 * 4));
    } else {
        // Вхід із внутрішньою підтяжкою Pull-up для прийому даних від цільового МК
        GPIOA->CRL |= (0x08 << (6 * 4));
        GPIOA->ODR |= SWDIO_PIN;
    }
}

// Керування станом індикаторних світлодіодів
void board_set_led_state(uint16_t led_pin, bool active) {
    if (active) {
        GPIOB->BRR = led_pin;   // Активний рівень - 0 (світлодіод увімкнено до GND)
    } else {
        GPIOB->BSRR = led_pin;  // Вимкнено - 1 (підтяжка до VCC)
    }
}
