#include <stdio.h>
#include <stdlib.h>
#include <iio.h>

int main(void) {
    struct iio_context *ctx = iio_create_default_context();
    if (!ctx) {
        perror("Не вдалося створити IIO контекст");
        return EXIT_FAILURE;
    }

    struct iio_device *dev = iio_context_find_device(ctx, "mpu6050");
    if (!dev) {
        dev = iio_context_find_device(ctx, "iio:device0");
    }

    if (!dev) {
        fprintf(stderr, "IIO пристрій не знайдено\n");
        iio_context_destroy(ctx);
        return EXIT_FAILURE;
    }

    struct iio_channel *chn_x = iio_device_find_channel(dev, "accel_x", false);
    struct iio_channel *chn_y = iio_device_find_channel(dev, "accel_y", false);
    struct iio_channel *chn_z = iio_device_find_channel(dev, "accel_z", false);

    if (chn_x) iio_channel_enable(chn_x);
    if (chn_y) iio_channel_enable(chn_y);
    if (chn_z) iio_channel_enable(chn_z);

    struct iio_buffer *buf = iio_device_create_buffer(dev, 256, false);
    if (!buf) {
        perror("Помилка створення буфера libiio");
        iio_context_destroy(ctx);
        return EXIT_FAILURE;
    }

    printf("Зчитування даних через libiio...\n");
    for (int i = 0; i < 5; ++i) {
        ssize_t ret = iio_buffer_refill(buf);
        if (ret < 0) {
            fprintf(stderr, "Помилка поповнення буфера: %d\n", (int)ret);
            break;
        }

        ptrdiff_t step = iio_buffer_step(buf);
        char *ptr = iio_buffer_start(buf);
        char *end = iio_buffer_end(buf);

        for (; ptr < end; ptr += step) {
            int16_t x_raw = 0, y_raw = 0, z_raw = 0;
            if (chn_x) iio_channel_read(chn_x, buf, &x_raw, sizeof(x_raw));
            if (chn_y) iio_channel_read(chn_y, buf, &y_raw, sizeof(y_raw));
            if (chn_z) iio_channel_read(chn_z, buf, &z_raw, sizeof(z_raw));
        }
        printf("Пакет %d оброблено успішно (байтів: %zd)\n", i, ret);
    }

    iio_buffer_destroy(buf);
    iio_context_destroy(ctx);
    return EXIT_SUCCESS;
}
