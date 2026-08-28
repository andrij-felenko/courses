static int my_adc_read_raw(struct iio_dev *indio_dev,
                           struct iio_chan_spec const *chan,
                           int *val, int *val2, long mask)
{
    struct my_adc_priv *priv = iio_priv(indio_dev);

    switch (mask) {
    case IIO_CHAN_INFO_RAW:
        mutex_lock(&priv->lock);
        *val = my_adc_hardware_read(priv, chan->channel);
        mutex_unlock(&priv->lock);
        return IIO_VAL_INT;

    case IIO_CHAN_INFO_SCALE:
        // Масштаб 0.805664 мВ (для 12-біт АЦП при 3.3 В опорної напруги)
        *val = 0;
        *val2 = 805664;
        return IIO_VAL_INT_PLUS_MICRO;

    case IIO_CHAN_INFO_OFFSET:
        *val = -100; // Апаратний зсув нуля
        return IIO_VAL_INT;

    default:
        return -EINVAL;
    }
}
