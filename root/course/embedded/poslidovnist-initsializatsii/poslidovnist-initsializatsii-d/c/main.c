#include <stdio.h>

#include "platform.h"
#include "sensor.h"

int main(void)
{
    sim_reset_board();
    printf("== підйом периферії ==\n");

    sensor_t devices[2] = {
        { .addr = 0x6A, .name = "гіроскоп польотного контролера", .critical = true,
          .boot_ms = 40U },
        { .addr = 0x6B, .name = "давач вологості",                .critical = false,
          .boot_ms = 15U },
    };

    /* Лінія живлення спільна, отже чекаємо на найповільніший чип */
    uint32_t rail_boot_ms = 0;
    for (unsigned i = 0; i < 2; ++i) {
        if (devices[i].boot_ms > rail_boot_ms) {
            rail_boot_ms = devices[i].boot_ms;
        }
    }

    sensor_power_guard_t guard;
    sensor_start_power_timer(&guard);

    /* Поки піднімається живлення, процесор працює: годує watchdog, крутить цикл */
    uint32_t idle_ticks = 0;
    while (!sensor_is_power_ready(&guard, rail_boot_ms)) {
        hw_watchdog_kick();
        idle_ticks++;
        delay_ms(1);
    }
    printf("живлення на режимі на %u мс, головний цикл провернувся %u разів\n",
           (unsigned)platform_get_millis(), (unsigned)idle_ticks);

    bool need_safe_state = false;
    for (unsigned i = 0; i < 2; ++i) {
        sensor_t *dev = &devices[i];
        printf("\n-- %s (адреса 0x%02X)\n", dev->name, dev->addr);

        init_result_t rc = sensor_bringup(dev);
        if (rc == INIT_OK) {
            bool ready = false;
            (void)sensor_data_ready(dev->addr, &ready);
            printf("   готовий зі спроби %u, DRDY=%d\n",
                   (unsigned)dev->attempts_used, (int)ready);
            continue;
        }

        printf("   ВІДМОВА після %u спроб: %s\n",
               (unsigned)dev->attempts_used, init_result_str(rc));

        if (dev->critical) {
            need_safe_state = true;
        } else {
            /* Некритичний давач: відліки маркуються невалідними, виріб працює далі */
            hw_fault_led(true);
            printf("   некритичний: дані позначено невалідними, робота триває\n");
        }
    }

    if (need_safe_state) {
        hw_actuators_disable();
        hw_fault_led(true);
        printf("\nКРИТИЧНИЙ давач не піднявся: приводи заблоковано, безпечний стан\n");
        return 1;
    }

    printf("\nсистема в штатному режимі на %u мс\n", (unsigned)platform_get_millis());
    return 0;
}
