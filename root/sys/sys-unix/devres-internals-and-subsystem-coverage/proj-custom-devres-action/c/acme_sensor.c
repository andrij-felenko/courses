// SPDX-License-Identifier: GPL-2.0
/*
 * acme_sensor.c — Драйвер датчика з повним керуванням ресурсами devres
 */

#include <linux/module.h>
#include <linux/platform_device.h>
#include <linux/io.h>
#include <linux/clk.h>
#include <linux/interrupt.h>
#include <linux/hwmon.h>
#include <linux/workqueue.h>
#include <linux/delay.h>
#include <linux/slab.h>

#define ACME_REG_CTRL       0x00
#define ACME_REG_STATUS     0x04
#define ACME_REG_DATA       0x08
#define ACME_CTRL_ENABLE    BIT(0)
#define ACME_CTRL_RESET     BIT(1)
#define ACME_STATUS_READY   BIT(0)

struct acme_sensor_priv {
	struct device *dev;
	void __iomem *regs;
	struct clk *clk;
	int irq;
	struct delayed_work poll_work;
	struct mutex lock;
	u32 cached_sample;
};

/* Власна дія: переведення заліза в стан низького споживання */
static void acme_hw_disable_action(void *data)
{
	struct acme_sensor_priv *priv = data;
	u32 val;

	/* Записуємо нуль у регістр контролю для зупинки вимірювань */
	val = readl(priv->regs + ACME_REG_CTRL);
	val &= ~ACME_CTRL_ENABLE;
	writel(val, priv->regs + ACME_REG_CTRL);

	dev_dbg(priv->dev, "Апаратну частину датчика вимкнено через devm-action\n");
}

/* Власна дія: зупинка та синхронізація робочої черги */
static void acme_cancel_work_action(void *data)
{
	struct acme_sensor_priv *priv = data;

	/* Гарантує, що жоден фоновий потік більше не звернеться до priv */
	cancel_delayed_work_sync(&priv->poll_work);
}

static void acme_poll_worker(struct work_struct *work)
{
	struct acme_sensor_priv *priv =
		container_of(work, struct acme_sensor_priv, poll_work.work);

	mutex_lock(&priv->lock);
	if (readl(priv->regs + ACME_REG_STATUS) & ACME_STATUS_READY)
		priv->cached_sample = readl(priv->regs + ACME_REG_DATA);
	mutex_unlock(&priv->lock);

	schedule_delayed_work(&priv->poll_work, msecs_to_jiffies(1000));
}

static irqreturn_t acme_irq_handler(int irq, void *dev_id)
{
	struct acme_sensor_priv *priv = dev_id;

	/* Швидка реакція на переривання готовності даних */
	schedule_delayed_work(&priv->poll_work, 0);
	return IRQ_HANDLED;
}

/* Динамічна фаза калібрування з використанням devres groups */
static int acme_calibrate_sensor(struct acme_sensor_priv *priv)
{
	struct device *dev = priv->dev;
	void *group_id;
	u32 *calib_buf;
	int ret = 0;

	/* Відкриваємо ізольовану групу ресурсів під тимчасові дані калібрування */
	group_id = devres_open_group(dev, NULL, GFP_KERNEL);
	if (!group_id)
		return -ENOMEM;

	calib_buf = devm_kmalloc(dev, 1024, GFP_KERNEL);
	if (!calib_buf) {
		devres_release_group(dev, group_id);
		return -ENOMEM;
	}

	/* Імітація читання калібрувальної таблиці з чіпа */
	calib_buf[0] = readl(priv->regs + ACME_REG_DATA);

	/* Якщо дані некоректні — відкочуємо групу */
	if (calib_buf[0] == 0xFFFFFFFF) {
		dev_err(dev, "Помилка калібрування датчика\n");
		ret = -EIO;
		devres_release_group(dev, group_id);
		return ret;
	}

	/* Якщо все добре — закриваємо групу або видаляємо тимчасовий буфер */
	devres_release_group(dev, group_id);
	return 0;
}

/* HWMON-інтерфейс читання температури */
static umode_t acme_hwmon_is_visible(const void *drvdata,
                                     enum hwmon_sensor_types type,
                                     u32 attr, int channel)
{
	return 0444;
}

static int acme_hwmon_read(struct device *dev, enum hwmon_sensor_types type,
                           u32 attr, int channel, long *val)
{
	struct acme_sensor_priv *priv = dev_get_drvdata(dev);

	mutex_lock(&priv->lock);
	*val = (long)priv->cached_sample * 1000;
	mutex_unlock(&priv->lock);

	return 0;
}

static const struct hwmon_channel_info *acme_hwmon_info[] = {
	HWMON_CHANNEL_INFO(temp, HWMON_T_INPUT),
	NULL
};

static const struct hwmon_ops acme_hwmon_ops = {
	.is_visible = acme_hwmon_is_visible,
	.read = acme_hwmon_read,
};

static const struct hwmon_chip_info acme_chip_info = {
	.ops = &acme_hwmon_ops,
	.info = acme_hwmon_info,
};

static int acme_sensor_probe(struct platform_device *pdev)
{
	struct device *dev = &pdev->dev;
	struct acme_sensor_priv *priv;
	struct device *hwmon_dev;
	int ret;

	/* 1. Виділення пам'яті для приватного стану */
	priv = devm_kzalloc(dev, sizeof(*priv), GFP_KERNEL);
	if (!priv)
		return -ENOMEM;

	priv->dev = dev;
	mutex_init(&priv->lock);
	INIT_DELAYED_WORK(&priv->poll_work, acme_poll_worker);
	platform_set_drvdata(pdev, priv);

	/* 2. Отримання та відображення діапазону регістрів MMIO */
	priv->regs = devm_platform_ioremap_resource(pdev, 0);
	if (IS_ERR(priv->regs))
		return PTR_ERR(priv->regs);

	/* 3. Отримання та ввімкнення тактового сигналу */
	priv->clk = devm_clk_get_enabled(dev, "sensor_clk");
	if (IS_ERR(priv->clk))
		return dev_err_probe(dev, PTR_ERR(priv->clk),
		                      "Не вдалося ввімкнути тактування\n");

	/* 4. Апаратне скидання та активація чіпа */
	writel(ACME_CTRL_RESET, priv->regs + ACME_REG_CTRL);
	usleep_range(1000, 2000);
	writel(ACME_CTRL_ENABLE, priv->regs + ACME_REG_CTRL);

	/* 5. Реєструємо дію зупинки апаратного модуля */
	ret = devm_add_action_or_reset(dev, acme_hw_disable_action, priv);
	if (ret)
		return ret;

	/* 6. Реєструємо дію зупинки фонової робочої черги */
	ret = devm_add_action_or_reset(dev, acme_cancel_work_action, priv);
	if (ret)
		return ret;

	/* 7. Виконання калібрування з локальною devres-групою */
	ret = acme_calibrate_sensor(priv);
	if (ret)
		return ret;

	/* 8. Отримання лінії переривання та реєстрація обробника */
	priv->irq = platform_get_irq(pdev, 0);
	if (priv->irq < 0)
		return priv->irq;

	ret = devm_request_irq(dev, priv->irq, acme_irq_handler,
	                       IRQF_TRIGGER_RISING, "acme_sensor", priv);
	if (ret)
		return dev_err_probe(dev, ret, "Не вдалося отримати IRQ %d\n", priv->irq);

	/* 9. Реєстрація пристрою в підсистемі HWMON */
	hwmon_dev = devm_hwmon_device_register_with_info(dev, "acme_sensor",
	                                                 priv, &acme_chip_info,
	                                                 NULL);
	if (IS_ERR(hwmon_dev))
		return PTR_ERR(hwmon_dev);

	/* Запуск фонового опитування */
	schedule_delayed_work(&priv->poll_work, msecs_to_jiffies(100));

	dev_info(dev, "Датчик acme_sensor успішно ініціалізовано\n");
	return 0;
}

static const struct of_device_id acme_sensor_of_match[] = {
	{ .compatible = "acme,temp-sensor-v1" },
	{ /* кінець таблиці */ }
};
MODULE_DEVICE_TABLE(of, acme_sensor_of_match);

static struct platform_driver acme_sensor_driver = {
	.probe = acme_sensor_probe,
	.driver = {
		.name = "acme-sensor",
		.of_match_table = acme_sensor_of_match,
	},
	/* Функція .remove відсутня: devres автоматично виконає повне очищення */
};
module_platform_driver(acme_sensor_driver);

MODULE_AUTHOR("Linux Driver Engineer");
MODULE_DESCRIPTION("Acme Hardware Sensor Driver with Full Devres Support");
MODULE_LICENSE("GPL");
