#include "user_interface.h"

void user_init(void) {
    // Отримання структури причин скидання від ROM-завантажувача
    struct rst_info *rtc_info = system_get_rst_info();

    if (rtc_info != NULL) {
        if (rtc_info->reason == REASON_WDT_RST || rtc_info->reason == REASON_SOFT_WDT_RST) {
            // Перезавантаження через спрацьовування сторожового таймера
            os_printf("Увага: виявлено скидання WDT! Код: %d\n", rtc_info->reason);
        } else if (rtc_info->reason == REASON_EXCEPTION_RST) {
            // Аварійний виняток у прошивці
            os_printf("Критичний виняток! EPC1: 0x%08x, Адреса: 0x%08x\n", 
                      rtc_info->epc1, rtc_info->excvaddr);
        } else if (rtc_info->reason == REASON_DEEPLIGHT_RESET) {
            // Нормальне пробудження з режиму deep-sleep
            os_printf("Успішне пробудження з Deep-Sleep\n");
        }
    }
}
