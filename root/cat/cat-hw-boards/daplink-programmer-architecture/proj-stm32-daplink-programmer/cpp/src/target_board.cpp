#include "target_board.h"

// Структура регістрів GPIO для низькорівневого керування периферією STM32
struct GPIO_TypeDef {
    volatile uint32_t MODER;   // Регістр режиму виводів
    volatile uint32_t OTYPER;  // Регістр типу виходу (Push-Pull / Open-Drain)
    volatile uint32_t OSPEEDR; // Регістр швидкості фронтів
    volatile uint32_t PUPDR;   // Регістр підтягувальних резисторів
    volatile uint32_t IDR;     // Вхідний регістр даних
    volatile uint32_t ODR;     // Вихідний регістр даних
    volatile uint32_t BSRR;    // Регістр встановлення/скидання бітів
    volatile uint32_t BRR;     // Регістр скидання бітів
};

static GPIO_TypeDef GPIOA_Inst;
static GPIO_TypeDef GPIOB_Inst;
static GPIO_TypeDef GPIOC_Inst;

GPIO_TypeDef* GPIOA = &GPIOA_Inst;
GPIO_TypeDef* GPIOB = &GPIOB_Inst;
GPIO_TypeDef* GPIOC = &GPIOC_Inst;

void TargetBoard::init() {
    // 1. Увімкнення тактування портів GPIOA, GPIOB, GPIOC
    // (на реальному залізі здійснюється через регістр RCC->APB2ENR або RCC->AHB1ENR)

    // 2. Налаштування виводу SWCLK як швидкого цифрового виходу Push-Pull
    PIN_SWCLK_PORT->MODER |= (1U << (5 * 2));     // General purpose output
    PIN_SWCLK_PORT->OSPEEDR |= (3U << (5 * 2));    // Very high speed (50 MHz)

    // 3. Налаштування виводу SWDIO за замовчуванням як вихід Push-Pull
    PIN_SWDIO_PORT->MODER |= (1U << (6 * 2));
    PIN_SWDIO_PORT->OSPEEDR |= (3U << (6 * 2));

    // 4. Налаштування виводу nRESET як Open-Drain з внутрішньою підтяжкою до VCC
    PIN_NRESET_PORT->MODER |= (1U << (0 * 2));
    PIN_NRESET_PORT->OTYPER |= PIN_NRESET_PIN;    // Open-Drain
    PIN_NRESET_PORT->PUPDR |= (1U << (0 * 2));     // Pull-up

    // 5. Конфігурація виводів напрямку буферів узгодження рівнів (Level Shifters)
    PIN_DIR_SWCLK_PORT->MODER |= (1U << (1 * 2)); // Direction SWCLK
    PIN_DIR_SWDIO_PORT->MODER |= (1U << (2 * 2)); // Direction SWDIO

    // Початковий стан буфера SWCLK: Вихід на цільовий МК
    PIN_DIR_SWCLK_PORT->BSRR = PIN_DIR_SWCLK_PIN;
    DIR_SWDIO_OUT();

    // 6. Ініціалізація світлодіодів індикації
    PIN_LED_CONNECTED_PORT->MODER |= (1U << (13 * 2));
    PIN_LED_RUNNING_PORT->MODER |= (1U << (14 * 2));
    setLedStatus(false, false);

    currentMode_ = SwdMode::Disconnected;
}

void TargetBoard::configureSwd(SwdMode mode) {
    currentMode_ = mode;
    if (mode == SwdMode::SwdMode) {
        // Увімкнення ліній SWCLK та SWDIO, встановлення початкових високих рівнів
        SWCLK_SET_HIGH();
        SWDIO_SET_HIGH();
        DIR_SWDIO_OUT();
    } else {
        // Переведення ліній у безпечний високоімпедансний стан (Hi-Z)
        PIN_SWCLK_PORT->MODER &= ~(3U << (5 * 2)); // Input mode
        PIN_SWDIO_PORT->MODER &= ~(3U << (6 * 2)); // Input mode
        DIR_SWDIO_IN();
    }
}

void TargetBoard::setSwdioDirection(bool outputDirection) {
    if (outputDirection) {
        // Перемикання напрямку шинного буфера та виводу МК на вихід
        DIR_SWDIO_OUT();
        PIN_SWDIO_PORT->MODER |= (1U << (6 * 2));
    } else {
        // Перемикання напрямку шинного буфера та виводу МК на вхід
        PIN_SWDIO_PORT->MODER &= ~(3U << (6 * 2));
        DIR_SWDIO_IN();
    }
}

void TargetBoard::setResetPin(bool assertReset) {
    if (assertReset) {
        NRESET_ASSERT();
    } else {
        NRESET_RELEASE();
    }
}

bool TargetBoard::isResetAsserted() const {
    return ((PIN_NRESET_PORT->IDR & PIN_NRESET_PIN) == 0U);
}

void TargetBoard::setLedStatus(bool connected, bool running) {
    if (connected) {
        PIN_LED_CONNECTED_PORT->BRR = PIN_LED_CONNECTED_PIN; // Active Low LED
    } else {
        PIN_LED_CONNECTED_PORT->BSRR = PIN_LED_CONNECTED_PIN;
    }

    if (running) {
        PIN_LED_RUNNING_PORT->BRR = PIN_LED_RUNNING_PIN;
    } else {
        PIN_LED_RUNNING_PORT->BSRR = PIN_LED_RUNNING_PIN;
    }
}

void TargetBoard::initUart(uint32_t baudRate) {
    // Налаштування альтернативних функцій виводів PA2 (TX) та PA3 (RX) під периферію USART1
    PIN_UART_TX_PORT->MODER |= (2U << (2 * 2)); // Alternate function mode
    PIN_UART_RX_PORT->MODER |= (2U << (3 * 2)); // Alternate function mode

    // Розрахунок дільника швидкості USARTDIV для заданого baudRate при частоті PCLK2
    (void)baudRate;
    (void)systemClockHz_;
}
