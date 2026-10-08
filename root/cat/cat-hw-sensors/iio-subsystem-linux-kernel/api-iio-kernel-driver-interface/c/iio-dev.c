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

	indio_dev->name = "my_sensor";
	indio_dev->dev.parent = &client->dev;
	indio_dev->modes = INDIO_DIRECT_MODE;
	indio_dev->info = &my_sensor_info;
	indio_dev->channels = my_sensor_channels;
	indio_dev->num_channels = ARRAY_SIZE(my_sensor_channels);

	ret = devm_iio_triggered_buffer_setup(&client->dev, indio_dev,
					      NULL, my_sensor_trigger_handler,
					      NULL);
	if (ret) {
		dev_err(&client->dev, "Помилка налаштування буфера: %d\n", ret);
		return ret;
	}

	ret = devm_iio_device_register(&client->dev, indio_dev);
	if (ret) {
		dev_err(&client->dev, "Помилка реєстрації IIO пристрою: %d\n", ret);
		return ret;
	}

	return 0;
}
