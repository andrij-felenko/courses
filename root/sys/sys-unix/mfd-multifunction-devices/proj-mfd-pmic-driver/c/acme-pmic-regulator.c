// drivers/regulator/acme-pmic-regulator.c
#include <linux/module.h>
#include <linux/init.h>
#include <linux/platform_device.h>
#include <linux/regmap.h>
#include <linux/regulator/driver.h>
#include <linux/regulator/of_regulator.h>
#include <linux/interrupt.h>

#define ACME_REG_BUCK1_CTRL  0x02
#define ACME_REG_BUCK2_CTRL  0x03
#define ACME_REG_LDO1_CTRL   0x04
#define ACME_REG_LDO2_CTRL   0x05

/* Стандартні операції керування через regmap */
static const struct regulator_ops acme_buck_ops = {
	.enable        = regulator_enable_regmap,
	.disable       = regulator_disable_regmap,
	.is_enabled    = regulator_is_enabled_regmap,
	.list_voltage  = regulator_list_voltage_linear,
	.map_voltage   = regulator_map_voltage_linear,
	.get_voltage_sel = regulator_get_voltage_sel_regmap,
	.set_voltage_sel = regulator_set_voltage_sel_regmap,
};

static const struct regulator_desc acme_regulators[] = {
	{
		.name           = "BUCK1",
		.of_match       = of_match_ptr("buck1"),
		.regulators_node= of_match_ptr("regulators"),
		.id             = 0,
		.ops            = &acme_buck_ops,
		.type           = REGULATOR_VOLTAGE,
		.owner          = THIS_MODULE,
		.min_uV         = 800000,   /* 0.8 В */
		.uV_step        = 25000,    /* 25 мВ на крок */
		.n_voltages     = 41,       /* 0.8В .. 1.8В */
		.enable_reg     = ACME_REG_BUCK1_CTRL,
		.enable_mask    = BIT(7),
		.vsel_reg       = ACME_REG_BUCK1_CTRL,
		.vsel_mask      = 0x3F,
	},
	{
		.name           = "BUCK2",
		.of_match       = of_match_ptr("buck2"),
		.regulators_node= of_match_ptr("regulators"),
		.id             = 1,
		.ops            = &acme_buck_ops,
		.type           = REGULATOR_VOLTAGE,
		.owner          = THIS_MODULE,
		.min_uV         = 800000,
		.uV_step        = 25000,
		.n_voltages     = 41,
		.enable_reg     = ACME_REG_BUCK2_CTRL,
		.enable_mask    = BIT(7),
		.vsel_reg       = ACME_REG_BUCK2_CTRL,
		.vsel_mask      = 0x3F,
	},
};

static irqreturn_t acme_buck_oc_irq_handler(int irq, void *data)
{
	struct regulator_dev *rdev = data;

	dev_warn(rdev_get_dev(rdev), "Зафіксовано перевантаження за струмом (Over-Current)!\n");
	regulator_notifier_call_chain(rdev, REGULATOR_EVENT_OVER_CURRENT, NULL);
	return IRQ_HANDLED;
}

static int acme_regulator_probe(struct platform_device *pdev)
{
	struct device *dev = &pdev->dev;
	struct regmap *regmap;
	struct regulator_config config = { };
	int i, irq, ret;

	/* Отримання дескриптора мапи регістрів від батьківського MFD */
	regmap = dev_get_regmap(dev->parent, NULL);
	if (!regmap) {
		dev_err(dev, "Не знайдено батьківський regmap\n");
		return -EINVAL;
	}

	config.dev = dev;
	config.regmap = regmap;

	for (i = 0; i < ARRAY_SIZE(acme_regulators); i++) {
		struct regulator_dev *rdev;

		rdev = devm_regulator_register(dev, &acme_regulators[i], &config);
		if (IS_ERR(rdev)) {
			dev_err(dev, "Помилка реєстрації регулятора %s: %pe\n",
				acme_regulators[i].name, rdev);
			return PTR_ERR(rdev);
		}

		/* Якщо визначено переривання перевантаження для BUCK1 */
		if (i == 0) {
			irq = platform_get_irq_byname_optional(pdev, "buck1_oc");
			if (irq > 0) {
				ret = devm_request_threaded_irq(dev, irq, NULL,
								acme_buck_oc_irq_handler,
								IRQF_ONESHOT,
								"acme-buck1-oc", rdev);
				if (ret < 0)
					dev_warn(dev, "Не вдалося отримати IRQ %d: %d\n", irq, ret);
			}
		}
	}

	return 0;
}

static const struct of_device_id acme_regulator_of_match[] = {
	{ .compatible = "acme,pmic800-regulator" },
	{ }
};
MODULE_DEVICE_TABLE(of, acme_regulator_of_match);

static struct platform_driver acme_regulator_driver = {
	.driver = {
		.name           = "acme-pmic-regulator",
		.of_match_table = acme_regulator_of_match,
	},
	.probe = acme_regulator_probe,
};
module_platform_driver(acme_regulator_driver);

MODULE_AUTHOR("Linux Kernel Engineer");
MODULE_DESCRIPTION("Regulator driver for ACME PMIC800");
MODULE_LICENSE("GPL");
