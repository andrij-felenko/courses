static int chip_read(struct device *dev, enum hwmon_sensor_types type,
                     u32 attr, int channel, long *val)
{
        struct chip_data *data = dev_get_drvdata(dev);
        u16 reg;
        int err;

        switch (type) {
        case hwmon_temp:
                err = chip_read_temp_reg(data, channel, attr, &reg);
                if (err)
                        return err;
                *val = ((s16)reg >> 7) * 500;   /* мілі°C */
                return 0;
        default:
                return -EOPNOTSUPP;
        }
}
