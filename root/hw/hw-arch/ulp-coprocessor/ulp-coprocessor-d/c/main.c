// Виконується на ядрі ULP-RISC-V (ESP-IDF).
// Компілюється окремо і завантажується в RTC-пам'ять до старту deep-sleep.
#include "ulp_riscv_utils.h"
#include "ulp_riscv_adc_ulp_core.h"

// Змінні в RTC-пам'яті — спільні для ULP і великого ядра.
uint32_t ulp_last_adc_value;
uint32_t ulp_alarm_count;

#define THRESHOLD_LOW   400   // ~15 °C на 12-бітному АЦП при 3.3 В
#define THRESHOLD_HIGH  700   // ~35 °C

int main(void) {
    // RTC-варіант читання АЦП: звичайний esp_adc у сні недоступний.
    uint32_t adc = ulp_riscv_adc_read_channel(ADC_UNIT_1, ADC_CHANNEL_6);
    ulp_last_adc_value = adc;

    if (adc < THRESHOLD_LOW || adc > THRESHOLD_HIGH) {
        ulp_alarm_count++;                    // поза вікном — є подія
        ulp_riscv_wakeup_main_processor();    // піднімаємо велике ядро
    }
    return 0;
    // Після return ulp_riscv_halt() викликається АВТОМАТИЧНО:
    // ULP паркується до наступного тіку RTC-таймера.
    // Свій while(1) чи явний halt тут не потрібні й шкідливі.
}
