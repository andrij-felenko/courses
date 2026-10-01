#include "user_interface.h"
#include "osapi.h"

void analyze_boot_reason(void) {
    struct rst_info *info = system_get_rst_info();
    
    os_printf("Код причини завантаження: %d\n", info->reason);
    
    if (info->reason == REASON_WDT_RST || info->reason == REASON_SOFT_WDT_RST) {
        os_printf("Перезавантаження викликано сторожовим таймером WDT\n");
    } else if (info->reason == REASON_EXCEPTION_RST) {
        os_printf("Аварійне переривання ядра! Cause: %d, EPC1: 0x%08x, VADDR: 0x%08x\n",
                  info->exccause, info->epc1, info->excvaddr);
    } else if (info->reason == REASON_DEEP_SLEEP_RESET) {
        os_printf("Пробудження з режиму глибокого сну\n");
    } else {
        os_printf("Звичайний запуск або апаратне скидання\n");
    }
}
