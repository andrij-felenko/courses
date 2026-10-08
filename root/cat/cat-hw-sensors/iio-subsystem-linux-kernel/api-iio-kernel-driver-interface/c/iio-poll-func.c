#include <linux/iio/buffer.h>
#include <linux/iio/trigger.h>
#include <linux/iio/triggered_buffer.h>
#include <linux/iio/trigger_consumer.h>

static irqreturn_t my_sensor_trigger_handler(int irq, void *p)
{
	struct iio_poll_func *pf = p;
	struct iio_dev *indio_dev = pf->indio_dev;
	struct my_sensor_state *st = iio_priv(indio_dev);
	struct {
		s16 channels[3];
		s64 ts __aligned(8);
	} scan;
	int ret;

	mutex_lock(&st->lock);
	ret = my_sensor_read_block(st, scan.channels, sizeof(scan.channels));
	mutex_unlock(&st->lock);

	if (ret == 0) {
		iio_push_to_buffers_with_timestamp(indio_dev, &scan,
						   iio_get_time_ns(indio_dev));
	}

	iio_trigger_notify_done(indio_dev->trig);
	return IRQ_HANDLED;
}
