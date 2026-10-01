#include <stdio.h>
#include "user_interface.h"

void check_reset_reason(void) {
    struct rst_info *rtc_info = system_get_rst_info();
    if (rtc_info != NULL) {
        if (rtc_info->reason == REASON_WDT_RST) {
            os_printf("Скидання через апаратний WDT!\n");
        } else if (rtc_info->reason == REASON_SOFT_WDT_RST) {
            os_printf("Скидання через програмний WDT!\n");
        } else if (rtc_info->reason == REASON_DEFAULT_RST) {
            os_printf("Звичайне включення живлення.\n");
        }
    }
}
