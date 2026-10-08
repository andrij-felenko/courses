#include <linux/module.h>
#include <linux/i2c.h>
#include <linux/iio/iio.h>
#include <linux/iio/sysfs.h>
#include <linux/iio/buffer.h>
#include <linux/iio/trigger_consumer.h>
#include <linux/iio/triggered_buffer.h>

struct my_sensor_state {
	struct i2c_client *client;
	struct mutex lock;
	s16 accel_data[3];
};

static const struct iio_chan_spec my_sensor_channels[] = {
	{
		.type = IIO_ACCEL,
		.modified = 1,
		.channel2 = IIO_MOD_X,
		.info_mask_separate = BIT(IIO_CHAN_INFO_RAW),
		.info_mask_shared_by_type = BIT(IIO_CHAN_INFO_SCALE),
		.scan_index = 0,
		.scan_type = {
			.sign = 's',
			.realbits = 16,
			.storagebits = 16,
			.endianness = IIO_CPU,
		},
	},
	{
		.type = IIO_ACCEL,
		.modified = 1,
		.channel2 = IIO_MOD_Y,
		.info_mask_separate = BIT(IIO_CHAN_INFO_RAW),
		.info_mask_shared_by_type = BIT(IIO_CHAN_INFO_SCALE),
		.scan_index = 1,
		.scan_type = {
			.sign = 's',
			.realbits = 16,
			.storagebits = 16,
			.endianness = IIO_CPU,
		},
	},
	{
		.type = IIO_ACCEL,
		.modified = 1,
		.channel2 = IIO_MOD_Z,
		.info_mask_separate = BIT(IIO_CHAN_INFO_RAW),
		.info_mask_shared_by_type = BIT(IIO_CHAN_INFO_SCALE),
		.scan_index = 2,
		.scan_type = {
			.sign = 's',
			.realbits = 16,
			.storagebits = 16,
			.endianness = IIO_CPU,
		},
	},
	IIO_CHAN_SOFT_TIMESTAMP(3),
};

static int my_sensor_read_raw(struct iio_dev *indio_dev,
			      struct iio_chan_spec const *chan,
			      int *val, int *val2, long mask)
{
	struct my_sensor_state *st = iio_priv(indio_dev);

	switch (mask) {
	case IIO_CHAN_INFO_RAW:
		mutex_lock(&st->lock);
		/* Зчитування сирого значення з регістру давача через I2C */
		*val = st->accel_data[chan->channel2 - IIO_MOD_X];
		mutex_unlock(&st->lock);
		return IIO_VAL_INT;
	case IIO_CHAN_INFO_SCALE:
		/* Масштаб 0.0039 м/с² на LSB (3900 мікроодиниць) */
		*val = 0;
		*val2 = 3900;
		return IIO_VAL_INT_PLUS_MICRO;
	default:
		return -EINVAL;
	}
}

static const struct iio_info my_sensor_info = {
	.read_raw = my_sensor_read_raw,
};

static irqreturn_t my_sensor_trigger_handler(int irq, void *p)
{
	struct iio_poll_func *pf = p;
	struct iio_dev *indio_dev = pf->indio_dev;
	struct my_sensor_state *st = iio_priv(indio_dev);
	u8 buf[16]; /* Буфер для кадрів даних та часової мітки */

	mutex_lock(&st->lock);
	/* Зчитування трьох осей акселерометра */
	i2c_master_recv(st->client, (char *)st->accel_data, 6);
	memcpy(buf, st->accel_data, 6);
	mutex_unlock(&st->lock);

	iio_push_to_buffers_with_timestamp(indio_dev, buf, pf->timestamp);
	iio_trigger_notify_done(indio_dev->trig);

	return IRQ_HANDLED;
}

static int my_sensor_probe(struct i2c_client *client)
{
	struct iio_dev *indio_dev;
	struct my_sensor_state *st;
	int ret;

	indio_dev = devm_iio_device_alloc(&client->dev, sizeof(*st));
	if (!indio_dev)
		return -ENOMEM;

	st = iio_priv(indio_dev);
	st->client = client;
	mutex_init(&st->lock);

	indio_dev->name = "my_accel_sensor";
	indio_dev->modes = INDIO_DIRECT_MODE;
	indio_dev->info = &my_sensor_info;
	indio_dev->channels = my_sensor_channels;
	indio_dev->num_channels = ARRAY_SIZE(my_sensor_channels);

	ret = devm_iio_triggered_buffer_setup(&client->dev, indio_dev,
					      iio_pollfunc_store_time,
					      my_sensor_trigger_handler,
					      NULL);
	if (ret)
		return ret;

	return devm_iio_device_register(&client->dev, indio_dev);
}
