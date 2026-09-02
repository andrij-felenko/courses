// Той самий прилад на Zephyr, але додаток на C++. Дерево пристроїв і черга
// ядра лишаються рідними макросами Zephyr: обгортати їх нічим і нічого.
#include "devices.hpp"

#include <zephyr/kernel.h>
#include <zephyr/logging/log.h>

LOG_MODULE_REGISTER(vitals, LOG_LEVEL_INF);

namespace {

constexpr int kSensorPriority = 5;
constexpr int kSensorPeriodMs = 200;

// DEVICE_DT_GET віддає адресу статичної структури — це стала вираз,
// тож обидва об'єкти ініціалізуються ще на етапі компіляції.
constinit app::Sensor g_sensor{DEVICE_DT_GET(DT_NODELABEL(temp_sensor))};
constinit app::Led g_status_led{GPIO_DT_SPEC_GET(DT_ALIAS(status_led), gpios)};

struct Reading {
    std::int64_t uptime_ms;
    double celsius;
};

} // namespace

K_MSGQ_DEFINE(readings_q, sizeof(Reading), 8, 4);

extern "C" void sensor_thread(void *, void *, void *)
{
    if (auto ready = g_sensor.ready(); !ready) {
        LOG_ERR("%s: %s", g_sensor.name(), app::to_string(ready.error()));
        return;
    }

    while (true) {
        auto value = g_sensor.read(SENSOR_CHAN_AMBIENT_TEMP);
        if (!value) {
            LOG_WRN("%s", app::to_string(value.error()));
            k_msleep(kSensorPeriodMs);
            continue;
        }

        const Reading reading{k_uptime_get(), *value};

        // Черга переповнилася — споживач відстав. Викидаємо найстаріше
        // значення: свіжий вимір цінніший за минулий.
        if (k_msgq_put(&readings_q, &reading, K_MSEC(10)) != 0) {
            Reading stale{};
            (void)k_msgq_get(&readings_q, &stale, K_NO_WAIT);
            (void)k_msgq_put(&readings_q, &reading, K_NO_WAIT);
            LOG_WRN("черга переповнена, старий вимір відкинуто");
        }

        k_msleep(kSensorPeriodMs);
    }
}

K_THREAD_DEFINE(sensor_tid, 1024, sensor_thread, NULL, NULL, NULL, kSensorPriority, 0, 0);

int main()
{
    if (auto configured = g_status_led.configure(); !configured) {
        LOG_ERR("світлодіод стану: %s", app::to_string(configured.error()));
        return -ENODEV;
    }
    if (auto ready = g_sensor.ready(); !ready) {
        LOG_ERR("%s: %s", g_sensor.name(), app::to_string(ready.error()));
        return -ENODEV;
    }

    Reading reading{};

    while (true) {
        if (k_msgq_get(&readings_q, &reading, K_SECONDS(2)) != 0) {
            LOG_ERR("два кола без даних — світлодіод у тривогу");
            g_status_led.set(true);
            continue;
        }

        LOG_INF("t = %d.%02d °C (uptime %lld мс)", static_cast<int>(reading.celsius),
                static_cast<int>(reading.celsius * 100) % 100, reading.uptime_ms);
        g_status_led.toggle();
    }

    return 0;
}
