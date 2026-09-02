/* Той самий прилад на Zephyr. Драйвера датчика тут немає взагалі: він
   приходить із дерева, а код працює з абстракцією sensor_* — і саме тому
   зміна чипа коштує правки .overlay, а не переписування модуля. */
#include <zephyr/kernel.h>
#include <zephyr/device.h>
#include <zephyr/drivers/gpio.h>
#include <zephyr/drivers/sensor.h>
#include <zephyr/logging/log.h>

LOG_MODULE_REGISTER(vitals, LOG_LEVEL_INF);

#define SENSOR_STACK_SIZE 1024
#define SENSOR_PRIORITY   5
#define SENSOR_PERIOD_MS  200

/* Обидва вузли беруться з DeviceTree на етапі компіляції: у прошивці це
   готовий покажчик на статичну структуру, жодного пошуку в рантаймі. */
static const struct device *const sensor_dev = DEVICE_DT_GET(DT_NODELABEL(temp_sensor));
static const struct gpio_dt_spec status_led = GPIO_DT_SPEC_GET(DT_ALIAS(status_led), gpios);

struct reading {
    int64_t uptime_ms;
    struct sensor_value temperature;
};

K_MSGQ_DEFINE(readings_q, sizeof(struct reading), 8, 4);

static void sensor_thread(void *a, void *b, void *c)
{
    ARG_UNUSED(a);
    ARG_UNUSED(b);
    ARG_UNUSED(c);

    if (!device_is_ready(sensor_dev)) {
        LOG_ERR("датчик не готовий — потік зупинено");
        return;
    }

    while (true) {
        struct reading r = { .uptime_ms = k_uptime_get() };
        int rc = sensor_sample_fetch(sensor_dev);

        if (rc != 0) {
            LOG_WRN("sensor_sample_fetch: %d", rc);
            k_msleep(SENSOR_PERIOD_MS);
            continue;
        }

        rc = sensor_channel_get(sensor_dev, SENSOR_CHAN_AMBIENT_TEMP, &r.temperature);
        if (rc != 0) {
            LOG_WRN("канал температури недоступний: %d", rc);
            k_msleep(SENSOR_PERIOD_MS);
            continue;
        }

        /* Черга переповнилася — споживач відстав. Викидаємо найстаріше
           значення: свіжий вимір цінніший за минулий. */
        if (k_msgq_put(&readings_q, &r, K_MSEC(10)) != 0) {
            struct reading stale;

            (void)k_msgq_get(&readings_q, &stale, K_NO_WAIT);
            (void)k_msgq_put(&readings_q, &r, K_NO_WAIT);
            LOG_WRN("черга переповнена, старий вимір відкинуто");
        }

        k_msleep(SENSOR_PERIOD_MS);
    }
}

K_THREAD_DEFINE(sensor_tid, SENSOR_STACK_SIZE, sensor_thread, NULL, NULL, NULL,
                SENSOR_PRIORITY, 0, 0);

int main(void)
{
    struct reading r;

    if (!device_is_ready(sensor_dev)) {
        LOG_ERR("немає датчика %s", sensor_dev->name);
        return -ENODEV;
    }
    if (!gpio_is_ready_dt(&status_led)) {
        LOG_ERR("немає світлодіода стану");
        return -ENODEV;
    }

    int rc = gpio_pin_configure_dt(&status_led, GPIO_OUTPUT_INACTIVE);

    if (rc != 0) {
        LOG_ERR("gpio_pin_configure_dt: %d", rc);
        return rc;
    }

    while (true) {
        if (k_msgq_get(&readings_q, &r, K_SECONDS(2)) != 0) {
            LOG_ERR("два кола без даних — світлодіод у тривогу");
            gpio_pin_set_dt(&status_led, 1);
            continue;
        }

        LOG_INF("t = %d.%02d °C (uptime %lld мс)", r.temperature.val1,
                r.temperature.val2 / 10000, r.uptime_ms);
        gpio_pin_toggle_dt(&status_led);
    }

    return 0;
}
