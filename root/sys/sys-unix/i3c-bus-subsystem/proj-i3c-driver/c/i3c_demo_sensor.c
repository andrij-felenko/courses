/*
 * i3c_demo_sensor.c - Драйвер I3C сенсора з підтримкою IBI та sysfs
 */

#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/slab.h>
#include <linux/workqueue.h>
#include <linux/sysfs.h>
#include <linux/i3c/device.h>

#define SENSOR_REG_CHIP_ID   0x00
#define SENSOR_REG_TEMP_DATA 0x02
#define SENSOR_REG_CTRL      0x10

struct i3c_demo_sensor_priv {
	struct i3c_device *i3cdev;
	struct work_struct ibi_work;
	u16 last_temp;
	u8 chip_id;
};

/* Обробник нижньої половини IBI переривання */
static void i3c_demo_ibi_work_handler(struct work_struct *work)
{
	struct i3c_demo_sensor_priv *priv =
		container_of(work, struct i3c_demo_sensor_priv, ibi_work);
	struct i3c_priv_xfer xfers[2];
	u8 reg_addr = SENSOR_REG_TEMP_DATA;
	u8 raw_data[2] = {0};
	int ret;

	/* Читання регістра температури після отримання IBI сигналізації */
	xfers[0].rnw = false;
	xfers[0].len = 1;
	xfers[0].data.out = &reg_addr;

	xfers[1].rnw = true;
	xfers[1].len = 2;
	xfers[1].data.in = raw_data;

	ret = i3c_device_do_priv_xfers(priv->i3cdev, xfers, 2);
	if (ret == 0) {
		priv->last_temp = (raw_data[0] << 8) | raw_data[1];
		dev_info(&priv->i3cdev->dev,
			 "IBI оброблено: нова температура = %u\n", priv->last_temp);
	} else {
		dev_err(&priv->i3cdev->dev, "Помилка читання регістра температури через I3C\n");
	}
}

/* Callback переривання верхньої половини IBI (атомарний контекст) */
static void i3c_demo_ibi_handler(struct i3c_device *i3cdev,
				 const struct i3c_ibi_payload *payload)
{
	struct i3c_demo_sensor_priv *priv = i3cdev_get_drvdata(i3cdev);

	if (payload->len > 0) {
		u8 mdb = ((u8 *)payload->data)[0];
		dev_dbg(&i3cdev->dev, "Отримано MDB байт IBI: 0x%02x\n", mdb);
	}

	/* Передаємо обробку у робочу чергу */
	schedule_work(&priv->ibi_work);
}

/* Sysfs атрибут для зчитування температури з простору користувача */
static ssize_t temperature_show(struct device *dev,
				struct device_attribute *attr, char *buf)
{
	struct i3c_device *i3cdev = dev_to_i3cdev(dev);
	struct i3c_demo_sensor_priv *priv = i3cdev_get_drvdata(i3cdev);

	return sysfs_emit(buf, "%u\n", priv->last_temp);
}
static DEVICE_ATTR_RO(temperature);

static struct attribute *i3c_demo_attrs[] = {
	&dev_attr_temperature.attr,
	NULL,
};
ATTRIBUTE_GROUPS(i3c_demo);

static int i3c_demo_probe(struct i3c_device *i3cdev)
{
	struct i3c_demo_sensor_priv *priv;
	struct i3c_ibi_setup ibi_req = {0};
	struct i3c_priv_xfer xfers[2];
	u8 reg_addr = SENSOR_REG_CHIP_ID;
	int ret;

	priv = devm_kzalloc(&i3cdev->dev, sizeof(*priv), GFP_KERNEL);
	if (!priv)
		return -ENOMEM;

	priv->i3cdev = i3cdev;
	i3cdev_set_drvdata(i3cdev, priv);
	INIT_WORK(&priv->ibi_work, i3c_demo_ibi_work_handler);

	/* Перевірка Chip ID пристрою */
	xfers[0].rnw = false;
	xfers[0].len = 1;
	xfers[0].data.out = &reg_addr;

	xfers[1].rnw = true;
	xfers[1].len = 1;
	xfers[1].data.in = &priv->chip_id;

	ret = i3c_device_do_priv_xfers(i3cdev, xfers, 2);
	if (ret) {
		dev_err(&i3cdev->dev, "Не вдалося зчитати Chip ID через I3C\n");
		return ret;
	}

	dev_info(&i3cdev->dev, "Успішно знайдено I3C сенсор Chip ID: 0x%02x\n", priv->chip_id);

	/* Налаштування та активація внутрішньосмугових переривань (IBI) */
	ibi_req.max_payload_len = 1;
	ibi_req.num_slots = 2;
	ibi_req.handler = i3c_demo_ibi_handler;

	ret = i3c_device_request_ibi(i3cdev, &ibi_req);
	if (ret == 0) {
		ret = i3c_device_enable_ibi(i3cdev);
		if (ret) {
			dev_warn(&i3cdev->dev, "Не вдалося увімкнути IBI переривання\n");
			i3c_device_free_ibi(i3cdev);
		} else {
			dev_info(&i3cdev->dev, "IBI переривання успішно активовано\n");
		}
	}

	return 0;
}

static void i3c_demo_remove(struct i3c_device *i3cdev)
{
	struct i3c_demo_sensor_priv *priv = i3cdev_get_drvdata(i3cdev);

	i3c_device_disable_ibi(i3cdev);
	i3c_device_free_ibi(i3cdev);
	cancel_work_sync(&priv->ibi_work);

	dev_info(&i3cdev->dev, "Драйвер I3C сенсора вивантажено\n");
}

/* Таблиця зіставлення за 48-бітним Provisional ID (PID) */
static const struct i3c_device_id i3c_demo_ids[] = {
	/* Виробник (MIPI Manuf ID), Part ID */
	I3C_DEVICE(0x01B0, 0x0042, NULL),
	{ /* Термінатор */ }
};
MODULE_DEVICE_TABLE(i3c, i3c_demo_ids);

static struct i3c_driver i3c_demo_driver = {
	.driver = {
		.name = "i3c_demo_sensor",
		.dev_groups = i3c_demo_groups,
	},
	.probe = i3c_demo_probe,
	.remove = i3c_demo_remove,
	.id_table = i3c_demo_ids,
};

module_i3c_driver(i3c_demo_driver);

MODULE_AUTHOR("Antigravity Engineer");
MODULE_DESCRIPTION("Демонстраційний драйвер I3C-сенсора для ядра Linux");
MODULE_LICENSE("GPL");
