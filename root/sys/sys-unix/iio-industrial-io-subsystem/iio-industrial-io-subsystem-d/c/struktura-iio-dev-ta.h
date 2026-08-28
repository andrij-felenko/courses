struct my_adc_priv {
    struct spi_device *spi;
    struct regmap *regmap;
    struct mutex lock;
    uint16_t buffer[8];
};

struct iio_dev *indio_dev;
struct my_adc_priv *priv;

// Виділення єдиного блоку пам'яті для iio_dev та приватного контексту
indio_dev = devm_iio_device_alloc(&spi->dev, sizeof(*priv));
if (!indio_dev)
    return -ENOMEM;

priv = iio_priv(indio_dev);
priv->spi = spi;
mutex_init(&priv->lock);
