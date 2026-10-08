/* Зчитування вибірок IIO через libiio (C) */
#include <stdio.h>
#include <iio.h>

int main(void)
{
    struct iio_context *ctx;
    struct iio_device *dev;
    struct iio_channel *rx_x;
    struct iio_buffer *buf;

    /* Створення локального контексту IIO */
    ctx = iio_create_local_context();
    if (!ctx) return -1;

    /* Пошук пристрою за ім'ям або індексом */
    dev = iio_context_find_device(ctx, "mpu6050");
    if (!dev) {
        iio_context_destroy(ctx);
        return -1;
    }

    /* Знаходження та активація каналу акселерометра */
    rx_x = iio_device_find_channel(dev, "accel_x", false);
    if (rx_x) iio_channel_enable(rx_x);

    /* Створення кільцевого буфера на 1024 вибірки */
    buf = iio_device_create_buffer(dev, 1024, false);
    if (!buf) {
        iio_context_destroy(ctx);
        return -1;
    }

    /* Наповнення буфера та зчитування даних */
    iio_buffer_refill(buf);

    /* Очищення ресурсів */
    iio_buffer_destroy(buf);
    iio_context_destroy(ctx);
    return 0;
}
