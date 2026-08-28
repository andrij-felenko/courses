static umode_t ms_is_visible(const void *drvdata, enum hwmon_sensor_types type,
                             u32 attr, int channel)
{
        if (type != hwmon_temp)
                return 0;

        switch (attr) {
        case hwmon_temp_input:
                return 0444;
        case hwmon_temp_max:
        case hwmon_temp_max_hyst:
                return 0644;
        default:
                return 0;
        }
}
