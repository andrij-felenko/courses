#include <zephyr/kernel.h>
#include <zephyr/drivers/gpio.h>
#include <zephyr/drivers/sensor.h>

// Отримання конфігурації з DeviceTree на етапі компіляції
static const struct gpio_dt_spec s_led = GPIO_DT_SPEC_GET(DT_ALIAS(status_led), gpios);
static const struct device *const s_sensor = DEVICE_DT_GET(DT_NODELABEL(temp_sensor));

// Оголошення черги повідомлень на рівні ядра Zephyr
K_MSGQ_DEFINE(sensor_msgq, sizeof(struct sensor_value), 10, 4);

void sensor_thread_entry(void *dummy1, void *dummy2, void *dummy3) {
    ARG_UNUSED(dummy1); ARG_UNUSED(dummy2); ARG_UNUSED(dummy3);

    struct sensor_value temp_val;

    if (!device_is_ready(s_sensor)) {
        return;
    }

    while (1) {
        // Зчитування сенсора через уніфікований API
        sensor_sample_fetch(s_sensor);
        sensor_channel_get(s_sensor, SENSOR_CHAN_AMBIENT_TEMP, &temp_val);

        // Відправка в чергу повідомлень Zephyr
        k_msgq_put(&sensor_msgq, &temp_val, K_MSEC(10));

        // Періодичний сон на 200 мс
        k_msleep(200);
    }
}

// Визначення статичного потоку Zephyr із власним стеком 1024 байти
K_THREAD_DEFINE(sensor_tid, 1024, sensor_thread_entry, NULL, NULL, NULL, 5, 0, 0);
