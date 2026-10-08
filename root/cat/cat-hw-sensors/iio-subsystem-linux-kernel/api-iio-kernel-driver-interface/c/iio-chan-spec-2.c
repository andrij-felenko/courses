static int my_sensor_read_raw(struct iio_dev *indio_dev,
			      struct iio_chan_spec const *chan,
			      int *val, int *val2, long mask)
{
	struct my_sensor_state *st = iio_priv(indio_dev);
	int ret;

	switch (mask) {
	case IIO_CHAN_INFO_RAW:
		mutex_lock(&st->lock);
		ret = my_sensor_read_reg(st, chan->address, val);
		mutex_unlock(&st->lock);
		if (ret)
			return ret;
		return IIO_VAL_INT;

	case IIO_CHAN_INFO_SCALE:
		if (chan->type == IIO_ACCEL) {
			/* Масштаб 0.00981 м/с² на один відлік LSB */
			*val = 0;
			*val2 = 9810;
			return IIO_VAL_INT_PLUS_MICRO;
		}
		return -EINVAL;

	case IIO_CHAN_INFO_OFFSET:
		if (chan->type == IIO_TEMP) {
			*val = 25; /* Зсув 25 градусів Цельсія */
			return IIO_VAL_INT;
		}
		return -EINVAL;

	default:
		return -EINVAL;
	}
}

static const struct iio_info my_sensor_info = {
	.read_raw = my_sensor_read_raw,
};
