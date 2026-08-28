static const struct i3c_device_id my_sensor_ids[] = {
	I3C_DEVICE(0x01B0, 0x0042, NULL),
	{ }
};
MODULE_DEVICE_TABLE(i3c, my_sensor_ids);

static struct i3c_driver my_sensor_driver = {
	.driver = {
		.name = "my_sensor",
	},
	.probe = my_sensor_probe,
	.remove = my_sensor_remove,
	.id_table = my_sensor_ids,
};
module_i3c_driver(my_sensor_driver);
