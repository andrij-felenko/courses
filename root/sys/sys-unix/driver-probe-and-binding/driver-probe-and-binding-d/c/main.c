static int sensor_probe(struct i2c_client *client)
{
	struct iio_dev *indio;
	struct sensor *st;
	int ret;

	indio = devm_iio_device_alloc(&client->dev, sizeof(*st));
	if (!indio)
		return -ENOMEM;
	st = iio_priv(indio);

	st->vdd = devm_regulator_get(&client->dev, "vdd");
	if (IS_ERR(st->vdd))
		return dev_err_probe(&client->dev, PTR_ERR(st->vdd),
				     "немає регулятора живлення\n");

	ret = i2c_smbus_read_byte_data(client, REG_WHO_AM_I);
	if (ret < 0)
		return ret;
	if (ret != CHIP_ID)
		return -ENODEV;

	return devm_iio_device_register(&client->dev, indio);
}
