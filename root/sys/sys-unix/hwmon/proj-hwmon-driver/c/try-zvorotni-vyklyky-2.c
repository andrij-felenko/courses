static int ms_read(struct device *dev, enum hwmon_sensor_types type,
                   u32 attr, int channel, long *val)
{
        struct minisens *data = dev_get_drvdata(dev);
        s16 raw;
        int ret;

        if (type != hwmon_temp)
                return -EOPNOTSUPP;

        switch (attr) {
        case hwmon_temp_input:
                ret = ms_read_temp(data, &raw);
                break;
        case hwmon_temp_max:
                ret = ms_read_reg(data, MS_REG_MAX, &raw);
                break;
        case hwmon_temp_max_hyst:
                ret = ms_read_reg(data, MS_REG_HYST, &raw);
                break;
        default:
                return -EOPNOTSUPP;
        }
        if (ret)
                return ret;

        *val = ms_reg_to_mc(raw);       /* мілі°C — одиниця задана типом каналу */
        return 0;
}

static int ms_write(struct device *dev, enum hwmon_sensor_types type,
                    u32 attr, int channel, long val)
{
        struct minisens *data = dev_get_drvdata(dev);
        int ret;
        u8 reg;

        if (type != hwmon_temp)
                return -EOPNOTSUPP;

        switch (attr) {
        case hwmon_temp_max:
                reg = MS_REG_MAX;
                break;
        case hwmon_temp_max_hyst:
                reg = MS_REG_HYST;
                break;
        default:
                return -EOPNOTSUPP;
        }

        mutex_lock(&data->lock);
        ret = i2c_smbus_write_word_swapped(data->client, reg, ms_mc_to_reg(val));
        mutex_unlock(&data->lock);
        return ret;
}
