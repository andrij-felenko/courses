#include "iio_virtual_sensor.h"
#include <linux/module.h>
#include <linux/init.h>
#include <linux/platform_device.h>
#include <linux/err.h>

MODULE_AUTHOR("Industrial I/O Developer");
MODULE_DESCRIPTION("Віртуальний драйвер інерційного давача для підсистеми IIO ядра Linux");
MODULE_LICENSE("GPL");

/* Масив специфікацій каналів пристрою IIO */
static const struct iio_chan_spec iio_virtual_channels[] = {
	{
		.type = IIO_ACCEL,
		.modified = 1,
		.channel2 = IIO_MOD_X,
		.info_mask_separate = BIT(IIO_CHAN_INFO_RAW),
		.info_mask_shared_by_type = BIT(IIO_CHAN_INFO_SCALE),
		.scan_index = VIRT_CHAN_ACCEL_X,
		.scan_type = {
			.sign = 's',
			.realbits = 16,
			.storagebits = 16,
			.endianness = IIO_CPU,
		},
	},
	{
		.type = IIO_ANGL_VEL,
		.modified = 1,
		.channel2 = IIO_MOD_Z,
		.info_mask_separate = BIT(IIO_CHAN_INFO_RAW),
		.info_mask_shared_by_type = BIT(IIO_CHAN_INFO_SCALE),
		.scan_index = VIRT_CHAN_GYRO_Z,
		.scan_type = {
			.sign = 's',
			.realbits = 16,
			.storagebits = 16,
			.endianness = IIO_CPU,
		},
	},
	IIO_CHAN_SOFT_TIMESTAMP(VIRT_CHAN_TIMESTAMP),
};

/**
 * iio_virtual_read_raw() - Зворотний виклик для читання параметрів через sysfs.
 * @indio_dev: Екземпляр IIO-пристрою.
 * @chan: Специфікація запитуваного каналу.
 * @val: Вказівник для повернення цілої частини значення.
 * @val2: Вказівник для повернення дробної частини значення (за потреби).
 * @mask: Тип запитуваної інформації (RAW значення або SCALE масштаб).
 *
 * Return: Тип повернутого значення IIO_VAL_* або від'ємний код помилки.
 */
static int iio_virtual_read_raw(struct iio_dev *indio_dev,
				struct iio_chan_spec const *chan,
				int *val, int *val2, long mask)
{
	struct iio_virtual_dev *st = iio_priv(indio_dev);
	int ret = -EINVAL;

	mutex_lock(&st->lock);

	switch (mask) {
	case IIO_CHAN_INFO_RAW:
		switch (chan->type) {
		case IIO_ACCEL:
			*val = st->accel_val;
			ret = IIO_VAL_INT;
			break;
		case IIO_ANGL_VEL:
			*val = st->gyro_val;
			ret = IIO_VAL_INT;
			break;
		default:
			ret = -EINVAL;
			break;
		}
		break;

	case IIO_CHAN_INFO_SCALE:
		*val = st->scale_val;
		*val2 = st->scale_micro;
		ret = IIO_VAL_INT_PLUS_MICRO;
		break;

	default:
		ret = -EINVAL;
		break;
	}

	mutex_unlock(&st->lock);
	return ret;
}

/**
 * iio_virtual_write_raw() - Зворотний виклик для запису параметрів через sysfs.
 * @indio_dev: Екземпляр IIO-пристрою.
 * @chan: Специфікація модифікованого каналу.
 * @val: Ціла частина нового значення.
 * @val2: Дробна частина нового значення.
 * @mask: Тип модифікованого параметра (RAW або SCALE).
 *
 * Return: 0 у разі успіху або від'ємний код помилки.
 */
static int iio_virtual_write_raw(struct iio_dev *indio_dev,
				 struct iio_chan_spec const *chan,
				 int val, int val2, long mask)
{
	struct iio_virtual_dev *st = iio_priv(indio_dev);
	int ret = 0;

	mutex_lock(&st->lock);

	switch (mask) {
	case IIO_CHAN_INFO_RAW:
		switch (chan->type) {
		case IIO_ACCEL:
			st->accel_val = (s16)val;
			break;
		case IIO_ANGL_VEL:
			st->gyro_val = (s16)val;
			break;
		default:
			ret = -EINVAL;
			break;
		}
		break;

	case IIO_CHAN_INFO_SCALE:
		st->scale_val = val;
		st->scale_micro = val2;
		break;

	default:
		ret = -EINVAL;
		break;
	}

	mutex_unlock(&st->lock);
	return ret;
}

static const struct iio_info iio_virtual_info = {
	.read_raw = iio_virtual_read_raw,
	.write_raw = iio_virtual_write_raw,
};

static struct platform_device *g_pdev;

/**
 * iio_virtual_init() - Точка входу модуля ядра Linux.
 *
 * Створює віртуальний platform_device, виділяє структуру IIO-пристрою,
 * ініціалізує контекст, тригерний буфер та реєструє пристрій у підсистемі IIO.
 *
 * Return: 0 у разі успіху або від'ємний код помилки.
 */
static int __init iio_virtual_init(void)
{
	struct iio_dev *indio_dev;
	struct iio_virtual_dev *st;
	int ret;

	g_pdev = platform_device_register_simple("iio_virtual_sensor", -1, NULL, 0);
	if (IS_ERR(g_pdev)) {
		pr_err("iio_virtual_sensor: не вдалося зареєструвати platform_device\n");
		return PTR_ERR(g_pdev);
	}

	indio_dev = devm_iio_device_alloc(&g_pdev->dev, sizeof(*st));
	if (!indio_dev) {
		pr_err("iio_virtual_sensor: не вдалося виділити пам'ять для iio_dev\n");
		ret = -ENOMEM;
		goto err_unregister_pdev;
	}

	st = iio_priv(indio_dev);
	mutex_init(&st->lock);

	/* Початкові значення параметрів давача */
	st->accel_val = 981;
	st->gyro_val = 0;
	st->scale_val = 0;
	st->scale_micro = 1000;

	indio_dev->name = "iio_virtual_sensor";
	indio_dev->modes = INDIO_DIRECT_MODE;
	indio_dev->info = &iio_virtual_info;
	indio_dev->channels = iio_virtual_channels;
	indio_dev->num_channels = ARRAY_SIZE(iio_virtual_channels);

	ret = iio_virtual_buffer_setup(indio_dev);
	if (ret) {
		pr_err("iio_virtual_sensor: помилка налаштування тригерного буфера: %d\n", ret);
		goto err_unregister_pdev;
	}

	ret = devm_iio_device_register(&g_pdev->dev, indio_dev);
	if (ret) {
		pr_err("iio_virtual_sensor: помилка реєстрації IIO пристрою: %d\n", ret);
		goto err_unregister_pdev;
	}

	pr_info("iio_virtual_sensor: модуль успішно завантажено та зареєстровано\n");
	return 0;

err_unregister_pdev:
	platform_device_unregister(g_pdev);
	return ret;
}

/**
 * iio_virtual_exit() - Точка виходу модуля ядра Linux.
 *
 * Видаляє platform_device, що автоматично звільняє всі ресурси devm.
 */
static void __exit iio_virtual_exit(void)
{
	platform_device_unregister(g_pdev);
	pr_info("iio_virtual_sensor: модуль успішно вивантажено\n");
}

module_init(iio_virtual_init);
module_exit(iio_virtual_exit);
