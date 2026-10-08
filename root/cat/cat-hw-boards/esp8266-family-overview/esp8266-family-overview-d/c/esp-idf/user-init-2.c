// Конфігурація режиму глибокого сну у середовищі Non-OS SDK
#include "ets_sys.h"
#include "osapi.h"
#include "user_interface.h"

void user_init(void) {
    // Ініціалізація послідовного порту для виводу відлагодження
    uart_div_modify(0, UART_CLK_FREQ / 115200);
    
    // Встановлення тривалості сну на 600 секунд (600 000 000 мікросекунд)
    uint64 sleep_time_us = 600000000ULL;
    
    // Налаштування внутрішнього таймера RTC для генерації імпульсу скидання на GPIO16
    system_deep_sleep_set_option(1); // 1 = увімкнути RF при наступному старті
    system_deep_sleep(sleep_time_us);
}
