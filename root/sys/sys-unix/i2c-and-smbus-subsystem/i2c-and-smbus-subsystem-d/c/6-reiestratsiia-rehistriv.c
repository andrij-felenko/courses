static const struct regmap_config bmp280_regmap_config = {
	.reg_bits = 8,
	.val_bits = 8,
	.max_register = 0xFF,
	.cache_type = REGCACHE_RBTREE,
};

static int bmp280_i2c_probe(struct i2c_client *client)
{
	struct regmap *regmap;
	unsigned int chip_id;
	int ret;

	regmap = devm_regmap_init_i2c(client, &bmp280_regmap_config);
	if (IS_ERR(regmap))
		return PTR_ERR(regmap);

	ret = regmap_read(regmap, 0xD0, &chip_id);
	if (ret < 0)
		return ret;

	if (chip_id != 0x58)
		return -ENODEV;

	return bmp280_common_probe(&client->dev, regmap);
}
