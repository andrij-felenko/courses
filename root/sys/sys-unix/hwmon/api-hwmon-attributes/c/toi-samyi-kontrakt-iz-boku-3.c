static const struct hwmon_channel_info * const lm_info[] = {
        HWMON_CHANNEL_INFO(chip, HWMON_C_UPDATE_INTERVAL | HWMON_C_REGISTER_TZ),
        HWMON_CHANNEL_INFO(temp,                     /* канал 0 */
                           HWMON_T_INPUT | HWMON_T_MAX | HWMON_T_MAX_ALARM,
                           HWMON_T_INPUT | HWMON_T_LABEL),   /* канал 1 */
        NULL
};

static const struct hwmon_ops lm_ops = {
        .is_visible  = lm_is_visible,
        .read        = lm_read,
        .read_string = lm_read_string,
        .write       = lm_write,
};

static const struct hwmon_chip_info lm_chip = {
        .ops  = &lm_ops,
        .info = lm_info,
};

struct device *hwmon;

hwmon = devm_hwmon_device_register_with_info(dev,        /* батьківський пристрій */
                                             "lm75",     /* name; ядро перевірить */
                                             data,       /* приватні дані драйвера */
                                             &lm_chip,
                                             NULL);      /* додаткові групи атрибутів */
if (IS_ERR(hwmon))
        return PTR_ERR(hwmon);
