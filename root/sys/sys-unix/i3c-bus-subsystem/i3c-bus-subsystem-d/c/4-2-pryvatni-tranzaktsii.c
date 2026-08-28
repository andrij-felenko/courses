static int my_sensor_read_reg(struct i3c_device *i3cdev, u8 reg, void *val, int len)
{
	struct i3c_priv_xfer xfers[2];

	/* Передача адреси регістра (Write) */
	xfers[0].rnw = false;
	xfers[0].len = 1;
	xfers[0].data.out = &reg;

	/* Прийом даних з регістра (Read) */
	xfers[1].rnw = true;
	xfers[1].len = len;
	xfers[1].data.in = val;

	return i3c_device_do_priv_xfers(i3cdev, xfers, 2);
}
