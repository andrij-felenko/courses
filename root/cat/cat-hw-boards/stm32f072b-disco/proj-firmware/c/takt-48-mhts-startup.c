#include "stm32f0xx.h"   // CMSIS: визначення RCC, GPIOC, SPI2, USART1, FLASH...

// Підняти системний такт з 8 МГц HSI до 48 МГц через PLL (×12 від HSI/2).
static void clock_48mhz(void) {
    // 1. СПЕРШУ — дозволити Flash чекати 1 такт. БЕЗ ЦЬОГО 48 МГц вішають чип.
    FLASH->ACR |= FLASH_ACR_LATENCY;            // LATENCY = 1 wait-state
    FLASH->ACR |= FLASH_ACR_PRFTBE;             // увімкнути буфер попередньої вибірки

    // 2. Налаштувати PLL: джерело = HSI/2 (це нуль у PLLSRC), множник = ×12.
    //    Код множника: PLLMUL = 0b1010 (десяткове 10) означає саме ×12.
    RCC->CFGR &= ~RCC_CFGR_PLLMUL;              // очистити старі біти множника
    RCC->CFGR |= RCC_CFGR_PLLMUL12;             // ×12

    // 3. Увімкнути PLL і дочекатися, поки він «захопиться» (стане стабільним).
    RCC->CR |= RCC_CR_PLLON;
    while (!(RCC->CR & RCC_CR_PLLRDY)) { }      // чекаємо прапорець готовності

    // 4. Перемкнути системний такт із HSI на PLL і дочекатися підтвердження.
    RCC->CFGR &= ~RCC_CFGR_SW;
    RCC->CFGR |= RCC_CFGR_SW_PLL;
    while ((RCC->CFGR & RCC_CFGR_SWS) != RCC_CFGR_SWS_PLL) { }
    // Тепер ядро йде на 48 МГц.
}
