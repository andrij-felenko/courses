#include "esp_system.h"
#include "user_interface.h"
#include "osapi.h"

void enter_deep_sleep_mode(uint64_t sleep_time_us) {
    // Налаштування режиму сну та виключення радіочастотного каскаду
    os_printf("Перехід у режим Deep Sleep на %llu мкс...\n", sleep_time_us);
    
    // Встановлення типу сну з вимкненням Wi-Fi RF перед засинанням
    wifi_set_sleep_type(LIGHT_SLEEP_T);
    
    // Виклик системної функції глибокого сну (вимагає з'єднання GPIO16 із RST)
    system_deep_sleep(sleep_time_us);
}

void check_power_supply_voltage(void) {
    // Внутрішній вимірювач VDD33 повертає значення у мілівольтах
    uint16_t vdd = system_get_vdd33();
    os_printf("Телеметрія живлення -> VCC: %u мВ\n", vdd);
    
    if (vdd < 3000) {
        os_printf("УВАГА: Напруга живлення VCC нижче 3.0 В! Ризик Brownout.\n");
    }
}
