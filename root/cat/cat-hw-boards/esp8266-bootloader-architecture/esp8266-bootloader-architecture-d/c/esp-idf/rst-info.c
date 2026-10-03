#include <stdio.h>
#include <stdint.h>
#include "user_interface.h"

/* Структура розшифровки причини апаратного скидання ESP8266 */
typedef struct {
    uint32_t reason_code;
    const char *description;
} reset_reason_desc_t;

static const reset_reason_desc_t reset_dictionary[] = {
    { REASON_DEFAULT_RST,      "Нормальне включення живлення (Power-On Reset)" },
    { REASON_WDT_RST,          "Спрацьовування апаратного вартового таймера (WDT)" },
    { REASON_EXCEPTION_RST,    "Фатальний виняток процесорного ядра (Kernel Panic)" },
    { REASON_SOFT_WDT_RST,     "Спрацьовування програмного вартового таймера" },
    { REASON_SOFT_RESTART,     "Програмне перезавантаження через system_restart()" },
    { REASON_DEEP_SLEEP_AWAKE, "Вихід із режиму глибокого сну (Deep Sleep)" },
    { REASON_EXT_SYS_RST,      "Зовнішнє апаратне скидання низьким рівнем на RST" }
};

/* Діагностика причини старту після зняття скидання */
void analyze_hardware_reset_cause(void) {
    struct rst_info *rtc_info = system_get_reset_info();
    
    printf("Діагностика живлення: Код rst cause = %d\n", rtc_info->reason);
    
    for (size_t i = 0; i < sizeof(reset_dictionary)/sizeof(reset_dictionary[0]); i++) {
        if (reset_dictionary[i].reason_code == rtc_info->reason) {
            printf("Причина старту: %s\n", reset_dictionary[i].description);
            break;
        }
    }
    
    if (rtc_info->reason == REASON_WDT_RST || rtc_info->reason == REASON_EXCEPTION_RST) {
        printf("УВАГА: Зафіксовано збій! Епц епіцентру: epc1=0x%08x, epc2=0x%08x\n", 
               rtc_info->epc1, rtc_info->epc2);
    }
}
