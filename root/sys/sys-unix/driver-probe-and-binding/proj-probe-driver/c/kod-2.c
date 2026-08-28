// SPDX-License-Identifier: GPL-2.0
#include <linux/device.h>
#include <linux/hwmon.h>
#include <linux/mod_devicetable.h>
#include <linux/module.h>
#include <linux/mutex.h>
#include <linux/platform_device.h>

#define DZHERELO "dzherelo"

struct termo {
	struct mutex lock;
	long         mk;      /* показ у мілліградусах Цельсія */
};

static umode_t termo_visible(const void *drvdata, enum hwmon_sensor_types type,
			     u32 attr, int channel)
{
	return 0444;
}

static int termo_read(struct device *dev, enum hwmon_sensor_types type,
		      u32 attr, int channel, long *val)
{
	struct termo *st = dev_get_drvdata(dev);

	mutex_lock(&st->lock);
	st->mk += 100;        /* заліза немає — показ вигадуємо */
	*val = st->mk;
	mutex_unlock(&st->lock);
	return 0;
}

static const struct hwmon_channel_info * const termo_info[] = {
	HWMON_CHANNEL_INFO(temp, HWMON_T_INPUT),
	NULL
};

static const struct hwmon_ops termo_hwmon_ops = {
	.is_visible = termo_visible,
	.read       = termo_read,
};

static const struct hwmon_chip_info termo_chip = {
	.ops  = &termo_hwmon_ops,
	.info = termo_info,
};

/* Ознаки, за якими шина зводить нас із пристроєм. Останній рядок обнулений:
   довжини таблиця не несе, і перебір спиняється саме на порожньому імені. */
static const struct platform_device_id termo_ids[] = {
	{ "termodatchyk",    30000 },
	{ "termodatchyk-v2", 25000 },
	{ }
};
MODULE_DEVICE_TABLE(platform, termo_ids);

static int termo_probe(struct platform_device *pdev)
{
	const struct platform_device_id *id = pdev->id_entry;
	struct device *dev = &pdev->dev;
	struct device *sup, *hwmon;
	struct termo *st;

	/* 1. Чи є постачальник — і чи він уже працює. Гонку тут ми свідомо
	      не закриваємо: найгірше, що буде, — один зайвий оберт черги. */
	sup = bus_find_device_by_name(&platform_bus_type, NULL, DZHERELO);
	if (!sup || !sup->driver) {
		put_device(sup);
		return dev_err_probe(dev, -EPROBE_DEFER,
				     "джерела «%s» ще немає\n", DZHERELO);
	}
	put_device(sup);

	/* 2. Свій стан. Усе через devm_ — драбинки прибирання не буде. */
	st = devm_kzalloc(dev, sizeof(*st), GFP_KERNEL);
	if (!st)
		return -ENOMEM;
	mutex_init(&st->lock);
	st->mk = id ? id->driver_data : 30000;   /* про NULL — у пастках */

	/* 3. І аж тепер назовні. Реєстрація остання не для краси: devm_
	      розмотує список у зворотному порядку, тож при відв'язці ми
	      відпишемося з підсистеми ПЕРШИМИ — раніше, ніж помре st. */
	hwmon = devm_hwmon_device_register_with_info(dev, "termodatchyk",
						     st, &termo_chip, NULL);
	if (IS_ERR(hwmon))
		return PTR_ERR(hwmon);

	dev_info(dev, "прив'язано, початок %ld мК\n", st->mk);
	return 0;
}

static struct platform_driver termo_driver = {
	.driver   = { .name = "termo" },   /* це ім'я з'явиться в drivers/ */
	.id_table = termo_ids,
	.probe    = termo_probe,
};
module_platform_driver(termo_driver);

MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("Вигаданий термодатчик на шині platform");
