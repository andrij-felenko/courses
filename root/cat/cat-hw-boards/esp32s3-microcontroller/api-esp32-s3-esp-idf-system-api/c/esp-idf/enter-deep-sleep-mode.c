#include "esp_sleep.h"
#include "driver/rtc_io.h"

// Змінна зберігається у пам'яті RTC SRAM під час режиму Deep-sleep
RTC_DATA_ATTR static uint32_t boot_count = 0;

void enter_deep_sleep_mode(void)
{
    boot_count++;

    // Налаштування пробудження від низького логічного рівня на RTC GPIO0
    esp_sleep_enable_ext0_wakeup(GPIO_NUM_0, 0);

    // Переведення мікроконтролера у режим глибокого сну
    esp_deep_sleep_start();
}
