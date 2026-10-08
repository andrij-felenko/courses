#include "iio_virtual_sensor.h"
#include <linux/iio/iio.h>
#include <linux/iio/buffer.h>
#include <linux/iio/trigger_consumer.h>
#include <linux/iio/triggered_buffer.h>

/**
 * iio_virtual_trigger_handler() - Потоковий обробник тригера IIO (потоковий контекст).
 * @irq: Номер переривання тригера.
 * @p: Контекст опитування IIO (struct iio_pollfunc).
 *
 * Функція викликається при спрацьовуванні тригера. Вона безпечно зчитує
 * поточні значення сенсорів, формує кадр вимірювання iio_virtual_scan_data
 * та відправляє його разом із точною часовою міткою у кільцевий буфер kfifo.
 *
 * Return: IRQ_HANDLED після успішної відправки даних.
 */
static irqreturn_t iio_virtual_trigger_handler(int irq, void *p)
{
	struct iio_pollfunc *pf = p;
	struct iio_dev *indio_dev = pf->indio_dev;
	struct iio_virtual_dev *st = iio_priv(indio_dev);
	struct iio_virtual_scan_data data;

	memset(&data, 0, sizeof(data));

	mutex_lock(&st->lock);
	data.accel = st->accel_val;
	data.gyro = st->gyro_val;
	mutex_unlock(&st->lock);

	/* Передача вимірювального кадру з часовою міткою у кільцевий буфер IIO */
	iio_push_to_buffers_with_timestamp(indio_dev, &data, pf->timestamp);

	/* Повідомлення підсистеми тригерів про завершення обробки */
	iio_trigger_notify_done(indio_dev->trig);

	return IRQ_HANDLED;
}

int iio_virtual_buffer_setup(struct iio_dev *indio_dev)
{
	return devm_iio_triggered_buffer_setup(indio_dev->dev.parent,
						indio_dev,
						iio_pollfunc_store_time,
						iio_virtual_trigger_handler,
						NULL);
}
