#include <linux/iio/iio.h>

#define MY_SENSOR_CHAN(_type, _mod, _index, _address) { \
	.type = _type, \
	.modified = 1, \
	.channel2 = _mod, \
	.address = _address, \
	.scan_index = _index, \
	.info_mask_separate = BIT(IIO_CHAN_INFO_RAW), \
	.info_mask_shared_by_type = BIT(IIO_CHAN_INFO_SCALE), \
	.scan_type = { \
		.sign = 's', \
		.realbits = 16, \
		.storagebits = 16, \
		.endianness = IIO_BE, \
	}, \
}

static const struct iio_chan_spec my_sensor_channels[] = {
	MY_SENSOR_CHAN(IIO_ACCEL, IIO_MOD_X, 0, 0x32),
	MY_SENSOR_CHAN(IIO_ACCEL, IIO_MOD_Y, 1, 0x34),
	MY_SENSOR_CHAN(IIO_ACCEL, IIO_MOD_Z, 2, 0x36),
	{
		.type = IIO_TEMP,
		.info_mask_separate = BIT(IIO_CHAN_INFO_RAW) |
				      BIT(IIO_CHAN_INFO_OFFSET) |
				      BIT(IIO_CHAN_INFO_SCALE),
		.scan_index = 3,
		.scan_type = {
			.sign = 's',
			.realbits = 12,
			.storagebits = 16,
			.endianness = IIO_CPU,
		},
	},
	IIO_CHAN_SOFT_TIMESTAMP(4),
};
