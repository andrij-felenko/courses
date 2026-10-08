#include <linux/module.h>
#include <linux/iio/iio.h>
#include <linux/iio/buffer.h>
#include <linux/iio/triggered_buffer.h>
#include <linux/iio/trigger_consumer.h>

/* Обробник нижньої половини тригера (bottom-half) */
static irqreturn_t my_sensor_trigger_handler(int irq, void *p)
{
    struct iio_poll_func *pf = p;
    struct iio_dev *indio_dev = pf->indio_dev;
    /* Буфер для збереження вибірок каналів + 64-бітної часової мітки */
    u16 data[8] __aligned(8);

    /* Зчитування сирих даних з давача через I2C/SPI */
    /* ... read_sensor_data(indio_dev, data) ... */

    /* Відправка кадру вибірки з часовою міткою в кільцевий буфер */
    iio_push_to_buffers_with_timestamp(indio_dev, data, pf->timestamp);

    /* Повідомлення підсистеми про завершення обробки тригера */
    iio_trigger_notify_done(indio_dev->trig);

    return IRQ_HANDLED;
}

/* Прив'язка буфера при ініціалізації драйвера */
static int my_sensor_setup_buffer(struct iio_dev *indio_dev)
{
    return devm_iio_triggered_buffer_setup(&indio_dev->dev,
                                            indio_dev,
                                            iio_pollfunc_store_time,
                                            my_sensor_trigger_handler,
                                            NULL);
}
