#define MS_CACHE_TTL (HZ / 2)           /* пів секунди */

struct minisens {
        struct i2c_client *client;
        struct mutex lock;              /* закриває і шину, і кеш */
        unsigned long stamp;            /* jiffies останнього успішного читання */
        bool valid;
        s16 raw;                        /* сире слово регістра температури */
};

static int ms_read_reg(struct minisens *data, u8 reg, s16 *out)
{
        int ret;

        mutex_lock(&data->lock);
        ret = i2c_smbus_read_word_swapped(data->client, reg);
        mutex_unlock(&data->lock);
        if (ret < 0)
                return ret;
        *out = (s16)ret;                /* функція вертає int: 0xE480 приїде як 58496 */
        return 0;
}

static int ms_read_temp(struct minisens *data, s16 *out)
{
        int ret = 0;

        mutex_lock(&data->lock);
        if (!data->valid || time_after(jiffies, data->stamp + MS_CACHE_TTL)) {
                ret = i2c_smbus_read_word_swapped(data->client, MS_REG_TEMP);
                if (ret < 0)
                        goto out;
                data->raw = (s16)ret;
                data->stamp = jiffies;
                data->valid = true;
                ret = 0;
        }
        *out = data->raw;
out:
        mutex_unlock(&data->lock);
        return ret;
}
