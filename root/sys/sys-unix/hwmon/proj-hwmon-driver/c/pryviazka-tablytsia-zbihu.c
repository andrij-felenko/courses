static int ms_probe(struct i2c_client *client)
{
        struct device *dev = &client->dev;
        struct minisens *data;
        struct device *hwmon;

        if (!i2c_check_functionality(client->adapter, I2C_FUNC_SMBUS_WORD_DATA))
                return -EOPNOTSUPP;

        data = devm_kzalloc(dev, sizeof(*data), GFP_KERNEL);
        if (!data)
                return -ENOMEM;

        data->client = client;
        mutex_init(&data->lock);

        hwmon = devm_hwmon_device_register_with_info(dev, "minisens", data,
                                                     &ms_chip_info, NULL);
        return PTR_ERR_OR_ZERO(hwmon);
}

static const struct i2c_device_id ms_ids[] = { { "minisens" }, { } };
MODULE_DEVICE_TABLE(i2c, ms_ids);

static const struct of_device_id ms_of_match[] = {
        { .compatible = "example,minisens" },
        { }
};
MODULE_DEVICE_TABLE(of, ms_of_match);

static struct i2c_driver ms_driver = {
        .driver = {
                .name           = "minisens",
                .of_match_table = ms_of_match,
        },
        .probe    = ms_probe,
        .id_table = ms_ids,
};
module_i2c_driver(ms_driver);
