#include <stdint.h>
#define ADC_STATUS  (*(volatile uint32_t *)0x3FF49000)  // біт 0 = готово
#define ADC_RESULT  (*(volatile uint32_t *)0x3FF49004)

// Опитуємо периферію, поки не з'явиться вибірка. У залізі це справжній
// АЦП; в емуляторі модель сама виставить біт готовності й підсуне число —
// той самий драйвер, але прогін повторюваний і без жодного чипа.
uint16_t adc_read_blocking(void) {
    while ((ADC_STATUS & 0x1u) == 0u) { /* busy-wait на готовність */ }
    return (uint16_t)(ADC_RESULT & 0x0FFFu);  // 12-бітний результат
}
