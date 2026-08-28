// drivers/mfd/acme-pmic-core.c
#include <linux/module.h>
#include <linux/init.h>
#include <linux/i2c.h>
#include <linux/regmap.h>
#include <linux/mfd/core.h>
#include <linux/interrupt.h>
#include <linux/of_platform.h>

#define ACME_REG_CHIP_ID     0x00
#define ACME_REG_POWER_CTRL  0x01
#define ACME_REG_INT_STATUS  0x10
#define ACME_REG_INT_MASK    0x11

#define ACME_CHIP_ID_VAL     0x80

/* Опис віртуальних апаратних переривань чипа */
enum acme_pmic_irqs {
	ACME_IRQ_BUCK1_OC,
	ACME_IRQ_RTC_ALARM,
	ACME_IRQ_PWRKEY,
	ACME_NUM_IRQS,
};

static const struct regmap_irq acme_irqs[] = {
	[ACME_IRQ_BUCK1_OC]  = { .mask = BIT(0), .reg_offset = 0 },
	[ACME_IRQ_RTC_ALARM] = { .mask = BIT(1), .reg_offset = 0 },
	[ACME_IRQ_PWRKEY]    = { .mask = BIT(2), .reg_offset = 0 },
};

static const struct regmap_irq_chip acme_irq_chip = {
	.name          = "acme-pmic-irq",
	.status_base   = ACME_REG_INT_STATUS,
	.mask_base     = ACME_REG_INT_MASK,
	.mask_invert   = false, /* 1 у масці вимикає лінію */
	.ack_base      = ACME_REG_INT_STATUS, /* Clear-on-write */
	.num_regs      = 1,
	.irqs          = acme_irqs,
	.num_irqs      = ARRAY_SIZE(acme_irqs),
};

/* Опис дочірніх комірок MFD */
static const struct mfd_cell acme_cells[] = {
	{
		.name          = "acme-pmic-regulator",
		.of_compatible = "acme,pmic800-regulator",
	},
	{
		.name          = "acme-pmic-rtc",
		.of_compatible = "acme,pmic800-rtc",
	},
	{
		.name          = "acme-pmic-onkey",
		.of_compatible = "acme,pmic800-onkey",
	},
};

static const struct regmap_config acme_regmap_config = {
	.reg_bits   = 8,
	.val_bits   = 8,
	.max_register = 0x20,
	.cache_type = REGCACHE_RBTREE,
};

static int acme_pmic_probe(struct i2c_client *i2c)
{
	struct device *dev = &i2c->dev;
	struct regmap *regmap;
	struct regmap_irq_chip_data *irq_data;
	unsigned int chip_id;
	int ret;

	/* 1. Створення мапи регістрів I2C */
	regmap = devm_regmap_init_i2c(i2c, &acme_regmap_config);
	if (IS_ERR(regmap)) {
		dev_err(dev, "Не вдалося ініціалізувати regmap: %pe\n", regmap);
		return PTR_ERR(regmap);
	}

	/* 2. Перевірка ідентифікатора кремнію */
	ret = regmap_read(regmap, ACME_REG_CHIP_ID, &chip_id);
	if (ret < 0) {
		dev_err(dev, "Помилка читання CHIP_ID: %d\n", ret);
		return ret;
	}

	if (chip_id != ACME_CHIP_ID_VAL) {
		dev_err(dev, "Невідомий чип ID 0x%02x (очікувався 0x%02x)\n",
			chip_id, ACME_CHIP_ID_VAL);
		return -ENODEV;
	}

	/* 3. Реєстрація демультиплексора переривань regmap-irq */
	if (i2c->irq > 0) {
		ret = devm_regmap_add_irq_chip(dev, regmap, i2c->irq,
					       IRQF_ONESHOT | IRQF_SHARED,
					       0, &acme_irq_chip, &irq_data);
		if (ret < 0) {
			dev_err(dev, "Помилка реєстрації regmap-irq: %d\n", ret);
			return ret;
		}
	}

	/* 4. Породження дочірніх платформених пристроїв */
	ret = devm_mfd_add_devices(dev, PLATFORM_DEVID_AUTO, acme_cells,
				   ARRAY_SIZE(acme_cells), NULL, 0,
				   irq_data ? regmap_irq_get_domain(irq_data) : NULL);
	if (ret < 0) {
		dev_err(dev, "Помилка додавання дочірніх комірок MFD: %d\n", ret);
		return ret;
	}

	dev_info(dev, "ACME PMIC800 успішно ініціалізовано\n");
	return 0;
}

static const struct of_device_id acme_of_match[] = {
	{ .compatible = "acme,pmic800" },
	{ }
};
MODULE_DEVICE_TABLE(of, acme_of_match);

static struct i2c_driver acme_pmic_driver = {
	.driver = {
		.name           = "acme-pmic-core",
		.of_match_table = acme_of_match,
	},
	.probe = acme_pmic_probe,
};
module_i2c_driver(acme_pmic_driver);

MODULE_AUTHOR("Linux Kernel Engineer");
MODULE_DESCRIPTION("Core MFD Driver for ACME PMIC800");
MODULE_LICENSE("GPL");
