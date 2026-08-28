static const struct hwmon_channel_info * const ms_info[] = {
        HWMON_CHANNEL_INFO(chip, HWMON_C_REGISTER_TZ),
        HWMON_CHANNEL_INFO(temp,
                           HWMON_T_INPUT | HWMON_T_MAX | HWMON_T_MAX_HYST),
        NULL
};

static const struct hwmon_ops ms_ops = {
        .is_visible = ms_is_visible,
        .read       = ms_read,
        .write      = ms_write,
};

static const struct hwmon_chip_info ms_chip_info = {
        .ops  = &ms_ops,
        .info = ms_info,
};
