#include <stdint.h>
#include <stdbool.h>
#include "ina219.h"

int main(void) {
    /* Ініціалізація датчика INA219 */
    ina219_init(INA219_I2C_ADDR_DEFAULT);

    /* Граничні пороги безпеки для модуля MB102 з LDO AMS1117-5.0V */
    Ina219Limits safety_limits = {
        .max_voltage_mv = 5500,  /* Не більше 5.5 В */
        .min_voltage_mv = 4500,  /* Не менше 4.5 В під навантаженням */
        .max_current_ma = 400    /* Максимум 400 мА для запобігання перегріву LDO */
    };

    Ina219Telemetry telemetry;

    /* Головний цикл моніторингу */
    while (1) {
        if (ina219_read_data(&telemetry)) {
            bool is_safe = ina219_check_safety(&telemetry, &safety_limits);
            if (!is_safe) {
                /*
                 * Аварійний стан: струм або напруга вийшли за допустимі межі.
                 * У реальній схемі тут розмикається силовий MOSFET або
                 * подається сигнал тривоги на зумер.
                 */
            }
        }
    }

    return 0;
}
