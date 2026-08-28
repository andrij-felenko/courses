// ============================================================================
// C99 / STM32 Low-Layer Drivers: Оптимізований енергетичний цикл
// ============================================================================
#include <stdint.h>
#include <stdbool.h>
#include "stm32l4xx_ll_bus.h"
#include "stm32l4xx_ll_gpio.h"
#include "stm32l4xx_ll_pwr.h"
#include "stm32l4xx_ll_adc.h"
#include "stm32l4xx_ll_dma.h"
#include "stm32l4xx_ll_utils.h"

#define SENSOR_POWER_PIN   LL_GPIO_PIN_4
#define SENSOR_POWER_PORT  GPIOA

// Увімкнення живлення сенсора через High-Side P-MOSFET (активний нуль)
static inline void sensor_power_enable(void) {
    LL_GPIO_ResetOutputPin(SENSOR_POWER_PORT, SENSOR_POWER_PIN);
}

static inline void sensor_power_disable(void) {
    LL_GPIO_SetOutputPin(SENSOR_POWER_PORT, SENSOR_POWER_PIN);
}

// Переведення невикористовуваних виводів у High-Z Analog для блокування витоків
void gpio_enter_low_power_mode(void) {
    LL_AHB2_GRP1_EnableClock(LL_AHB2_GRP1_PERIPH_GPIOB);
    // Конфігурація порту B в аналоговий режим (усі 16 пінів)
    GPIOB->MODER = 0xFFFFFFFF; // 11 = Analog Mode
    GPIOB->PUPDR = 0x00000000; // 00 = No Pull-up, No Pull-down
}

// Запуск автономного зчитування АЦП з автоматичним переходом ядра в сон
void start_adc_autonomous_measurement(uint32_t *dest_buffer, uint32_t length) {
    sensor_power_enable();
    LL_mDelay(1); // Короткий час на встановлення живлення сенсора

    // Налаштування каналу DMA для автоматичного перенесення результатів
    LL_DMA_ConfigAddresses(DMA1, LL_DMA_CHANNEL_1,
                           LL_ADC_DMA_GetRegAddr(ADC1, LL_ADC_DMA_REG_REGULAR_DATA),
                           (uint32_t)dest_buffer,
                           LL_DMA_DIRECTION_PERIPH_TO_MEMORY);
    LL_DMA_SetDataLength(DMA1, LL_DMA_CHANNEL_1, length);
    LL_DMA_EnableIT_TC(DMA1, LL_DMA_CHANNEL_1);
    LL_DMA_EnableChannel(DMA1, LL_DMA_CHANNEL_1);

    // Запуск АЦП та переведення ядра у режим Sleep (WFI)
    LL_ADC_REG_StartConversion(ADC1);
    
    // Ядро засинає; периферія оцифровує дані в RAM автономно
    __WFI();

    // Після завершення передачі DMA переривання розбудить ядро
    sensor_power_disable();
}
