struct i2c_driver {
	unsigned int class;
	int (*probe)(struct i2c_client *client);
	void (*remove)(struct i2c_client *client);
	void (*shutdown)(struct i2c_client *client);
	void (*alert)(struct i2c_client *client, enum i2c_alert_protocol protocol,
		      unsigned int data);

	int (*detect)(struct i2c_client *client, struct i2c_board_info *info);
	const unsigned short *address_list;
	struct list_head clients;

	struct device_driver driver;
	const struct i2c_device_id *id_table;
};
