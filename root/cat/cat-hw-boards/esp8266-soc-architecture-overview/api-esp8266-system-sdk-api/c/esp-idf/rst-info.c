// Приклад системної діагностики причини перезавантаження в C (Non-OS SDK)
#include "c_types.h"
#include "osapi.h"
#include "user_interface.h"

void print_system_diagnostics(void) {
    // 1. Отримання версії SDK та частоти CPU
    os_printf("Версія SDK: %s\n", system_get_sdk_version());
    os_printf("Тактова частота CPU: %u МГц\n", system_get_cpu_freq());

    // 2. Зчитування структури причин перезавантаження
    struct rst_info *rtc_info = system_get_rst_info();
    if (rtc_info == NULL) return;

    os_printf("--- ДІАГНОСТИКА ПЕРЕЗАВАНТАЖЕННЯ ---\n");
    os_printf("Код причини (reason): %u\n", rtc_info->reason);

    switch (rtc_info->reason) {
        case REASON_DEFAULT_RST:
            os_printf("Причина: Звичайне включення живлення (Power-On)\n");
            break;
        case REASON_WDT_RST:
            os_printf("УВАГА: Спрацював апаратний Hard WDT!\n");
            break;
        case REASON_EXCEPTION_RST:
            os_printf("КРИТИЧНО: Fatal Exception! exccause=%u, epc1=0x%08x, excvaddr=0x%08x\n",
                      rtc_info->exccause, rtc_info->epc1, rtc_info->excvaddr);
            break;
        case REASON_SOFT_WDT_RST:
            os_printf("УВАГА: Спрацював програмний Soft WDT!\n");
            break;
        case REASON_SOFT_RESTART:
            os_printf("Причина: Програмний перезапуск (system_restart)\n");
            break;
        default:
            os_printf("Інша причина перезавантаження\n");
            break;
    }
}
