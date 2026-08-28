/* Як драйвер ядра знаходить свій пристрій із Device Tree */
static const struct of_device_id tmp102_of_match[] = {
    { .compatible = "ti,tmp102" },
    { .compatible = "national,lm75" },
    { /* кінець таблиці */ }
};
MODULE_DEVICE_TABLE(of, tmp102_of_match);

static struct i2c_driver tmp102_driver = {
    .driver = {
        .name = "tmp102",
        .of_match_table = tmp102_of_match,
    },
    .probe = tmp102_probe,
    .remove = tmp102_remove,
};
