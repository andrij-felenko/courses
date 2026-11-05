#include "stm32f4xx.h"
#include <stdint.h>

// Визначення масок виводів для порта GPIOA
#define BITBANG_SCK_PIN   (1U << 5)  // PA5: SCK (Clock)
#define BITBANG_MOSI_PIN  (1U << 7)  // PA7: MOSI (Master Out Slave In)
#define BITBANG_MISO_PIN  (1U << 6)  // PA6: MISO (Master In Slave Out)

// Ініціалізація модуля DWT для точних затримок
void bitbang_dwt_init(void) {
    CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
    DWT->CYCCNT = 0;
    DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;
}

// Затримка у тактах процесора за допомогою DWT
static inline void bitbang_delay_ticks(uint32_t ticks) {
    uint32_t start = DWT->CYCCNT;
    while ((DWT->CYCCNT - start) < ticks) {
        __NOP();
    }
}

// Атомарна передача та прийом байта за протоколом Bit-bang SPI (Mode 0)
uint8_t bitbang_spi_transfer_byte(uint8_t tx_byte, uint32_t delay_ticks) {
    uint8_t rx_byte = 0;
    
    // Вхід у критичну секцію - блокування переривань для збереження детермінізму
    uint32_t primask = __get_PRIMASK();
    __disable_irq();

    for (int8_t i = 7; i >= 0; i--) {
        // 1. Встановлення біта даних на лінії MOSI через атомарний регістр BSRR
        if (tx_byte & (1U << i)) {
            GPIOA->BSRR = BITBANG_MOSI_PIN;        // Set HIGH (молодші 16 біт)
        } else {
            GPIOA->BSRR = (BITBANG_MOSI_PIN << 16); // Set LOW (старші 16 біт)
        }

        // Час встановлення даних (t_setup)
        bitbang_delay_ticks(delay_ticks);

        // 2. Формування наростаючого фронту SCK (Latch data)
        GPIOA->BSRR = BITBANG_SCK_PIN;

        // Час утримання високого рівня стробу (t_high)
        bitbang_delay_ticks(delay_ticks);

        // 3. Зчитування вхідного біта з MISO через регістр IDR
        if (GPIOA->IDR & BITBANG_MISO_PIN) {
            rx_byte |= (1U << i);
        }

        // 4. Формування спадного фронту SCK
        GPIOA->BSRR = (BITBANG_SCK_PIN << 16);

        // Час утримання низького рівня стробу (t_low)
        bitbang_delay_ticks(delay_ticks);
    }

    // Вихід з критичної секції - відновлення стану переривань
    if (!primask) {
        __enable_irq();
    }

    return rx_byte;
}
