#include <linux/module.h>
#include <linux/i2c.h>
#include <linux/iio/iio.h>

struct my_sensor_state {
	struct i2c_client *client;
	struct mutex lock; /* захист внутрішнього стану та шини I2C */
};

static int my_sensor_probe(struct i2c_client *client)
{
	struct iio_dev *indio_dev;
	struct my_sensor_state *st;

	/* Виділення пам'яті під iio_dev та приватний контекст драйвера */
	indio_dev = devm_iio_device_alloc(&client->dev, sizeof(*st));
	if (!indio_dev)
		return -ENOMEM;

	st = iio_priv(indio_dev);
	st->client = client;
	mutex_init(&st->lock);

	indio_dev->name = "my_sensor";
	indio_dev->modes = INDIO_DIRECT_MODE;

	return 0;
}
