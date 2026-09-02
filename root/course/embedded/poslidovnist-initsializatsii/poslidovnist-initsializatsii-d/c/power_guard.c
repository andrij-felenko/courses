#include "platform.h"
#include "sensor.h"

/*
 * Блокувати процесор на 35-100 мс не можна: за цей час не годується сторожовий
 * таймер і губляться швидкі події. Тому подачу живлення лише позначаємо міткою
 * часу, а факт виходу на режим перевіряємо в головному циклі.
 */
void sensor_start_power_timer(sensor_power_guard_t *guard)
{
    hw_power_rail_enable(true);
    guard->power_on_timestamp = platform_get_millis();
    guard->power_stable = false;
}

bool sensor_is_power_ready(sensor_power_guard_t *guard, uint32_t required_boot_ms)
{
    if (guard->power_stable) {
        return true; /* один раз вийшли на режим — далі не перевіряємо */
    }

    /*
     * Різниця беззнакових 32-бітних лічильників лишається правильною і після
     * переповнення millis (через ~49 діб), тому порівнюємо саме різницю,
     * а не "now >= timestamp + boot".
     */
    uint32_t elapsed = platform_get_millis() - guard->power_on_timestamp;
    if (elapsed >= required_boot_ms) {
        guard->power_stable = true;
        return true;
    }
    return false;
}

void sensor_power_off(sensor_power_guard_t *guard)
{
    hw_power_rail_enable(false);
    guard->power_stable = false;
    guard->power_on_timestamp = platform_get_millis();
}
