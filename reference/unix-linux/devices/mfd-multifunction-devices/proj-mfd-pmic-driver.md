# ⚙️ Реалізація MFD-драйвера PMIC та дочірнього регулятора на платформі

Цей практичний проект демонструє повну реалізацію дворівневого стека драйверів для мікросхеми керування живленням (PMIC): головного драйвера підсистеми MFD на шині I2C із демультиплексуванням переривань через `regmap-irq`, а також спеціалізованого дочірнього платформеного драйвера регуляторів напруги, який отримує спільний доступ до карти регістрів.

## 1. Архітектурна постановка завдання

Розглядається типова апаратна мікросхема PMIC (умовна назва `acme,pmic800`), підключена до системи на кристалі (SoC) через шину I2C за адресою `0x34` та одну фізичну лінію переривання `INT#` (активний низький рівень).

Мікросхема містить у собі:
1. **Регулятори напруги:** Два імпульсних BUCK-перетворювачі (0.8 В – 1.8 В із кроком 25 мВ) та два лінійних LDO-стабілізатори (1.8 В – 3.3 В).
2. **Годинник реального часу (RTC):** Із підтримкою встановлення дати та виклику переривання будильника.
3. **Кнопку живлення (ONKEY):** Фіксує короткі та довгі натискання.
4. **Вбудований контролер переривань:** 8-бітний регістр статусу (`0x10`) та маски (`0x11`), що сигналізує про події окремих блоків.

Розробка розбивається на дві ізольовані частини:
- Батьківський драйвер ядра MFD (`drivers/mfd/acme-pmic-core.c`), який створює мапу регістрів, домен віртуальних переривань та реєструє комірки `mfd_cell`.
- Дочірній драйвер регуляторів (`drivers/regulator/acme-pmic-regulator.c`), який взаємодіє з підсистемою `regulator` ядра Linux.

## 2. Карта регістрів та переривань чипа

Внутрішня пам'ять конфігурації мікросхеми розбита на функціональні зони з 8-бітною адресацією та 8-бітними значеннями даних:

```
Регістри чипа ACME PMIC800:
0x00: CHIP_ID (значення 0x80)
0x01: POWER_CTRL (біт 0: головне вимкнення живлення)
0x02: BUCK1_CTRL (біт 7: ENABLE, біти [5:0]: VSEL)
0x03: BUCK2_CTRL (біт 7: ENABLE, біти [5:0]: VSEL)
0x04: LDO1_CTRL  (біт 7: ENABLE, біти [4:0]: VSEL)
0x05: LDO2_CTRL  (біт 7: ENABLE, біти [4:0]: VSEL)
0x10: INT_STATUS (біт 0: BUCK1_OC, біт 1: RTC_ALARM, біт 2: PWRKEY)
0x11: INT_MASK   (1 — замасковано, 0 — дозволено)
```

Регістр `0x10` працює за схемою запису одиниці для очищення (Write-1-to-Clear, W1C): коли внутрішній компаратор фіксує перевантаження за струмом на каналі BUCK1, апаратна логіка виставляє біт 0 у `1` та опускає фізичну лінію `INT#` до нуля. Після зчитування статусу драйвер повинен записати `0x01` у регістр `0x10`, щоб зняти переривання.

## 3. Батьківський MFD драйвер (`acme-pmic-core.c`)

Батьківський драйвер виконує чотири послідовні задачі: ініціалізує I2C `regmap`, перевіряє сумісність зашитого в кремній ідентифікатора, розгортає `regmap_irq_chip` для демультиплексування ліній переривання та породжує дочірні вузли платформи через виклик `devm_mfd_add_devices()`.

```c
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
```

### 3.1. Розбір механізму зондування MFD

У функції `acme_pmic_probe` слід звернути увагу на послідовність дій ядра:
- Функція `devm_regmap_init_i2c()` створює екземпляр `struct regmap`, що огортає стандартні I2C-транзакції у м'ютекс блокування та вмикає кешування на основі червоно-чорного дерева (`REGCACHE_RBTREE`).
- Масив `acme_irqs` задає відносне зміщення бітів для кожного апаратного переривання. Структура `acme_irq_chip` зв'язує цей масив із регістрами `status_base` та `mask_base`.
- Функція `devm_regmap_add_irq_chip()` створює власний домен переривань (`struct irq_domain`), реєструє потоковий обробник переривання верхнього рівня на фізичній лінії `i2c->irq` і повертає непрозорий дескриптор `irq_data`.
- Виклик `devm_mfd_add_devices()` обходить масив `acme_cells`. Для кожної комірки він виділяє структуру `struct platform_device`, зіставляє поле `of_compatible` із відповідним дочірнім вузлом Device Tree, призначає поле `dev.parent` на батьківський `i2c_client->dev` та реєструє пристрій на платформеній шині ядра.

## 4. Дочірній драйвер регуляторів (`acme-pmic-regulator.c`)

Дочірній драйвер реєструється на віртуальній шині `platform_bus_type`. Він витягує батьківський `struct regmap` через виклик `dev_get_regmap(pdev->dev.parent, NULL)` та реєструє регулятори у підсистемі `regulator`.

```c
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
```

### 4.1. Розбір роботи дочірнього драйвера регуляторів

У цьому драйвері реалізовано ключові переваги абстракцій ядра:
1. **Повна незалежність від фізичної шини:** Драйвер не містить жодного виклику функцій I2C (`i2c_smbus_read_byte` чи `i2c_transfer`). Він взаємодіє виключно через абстрактний інтерфейс `struct regmap`. Завдяки цьому той самий код регулятора може без змін працювати з версією чипа на шині SPI або I3C.
2. **Використання універсальних помічників Regmap:** Замість написання власних функцій читання бітів вибору напруги (VSEL) та ввімкнення (ENABLE), таблиця операцій `acme_buck_ops` посилається на готові функції ядра: `regulator_enable_regmap`, `regulator_set_voltage_sel_regmap`, `regulator_list_voltage_linear`. Вони самостійно рахують значення бітів за формулою:

```
V = min_uV + selector × uV_step
```

3. **Отримання віртуального переривання:** Виклик `platform_get_irq_byname_optional(pdev, "buck1_oc")` автоматично транслює назву переривання через дерево Device Tree до віртуального номера переривання Linux у домені `regmap_irq_chip`. Обробник `acme_buck_oc_irq_handler` реєструється як потоковий обробник (`devm_request_threaded_irq`), що дозволяє надсилати сповіщення через ланцюжок `regulator_notifier_call_chain`.

## 5. Опис у дереві пристроїв (Device Tree DTS)

Вузол PMIC розміщується всередині відповідного I2C-контролера, а його підвузли містять налаштування споживачів:

```dts
&i2c1 {
	status = "okay";
	clock-frequency = <400000>;

	pmic: pmic@34 {
		compatible = "acme,pmic800";
		reg = <0x34>;
		interrupt-parent = <&gpio1>;
		interrupts = <24 IRQ_TYPE_LEVEL_LOW>;
		interrupt-controller;
		#interrupt-cells = <2>;

		regulators: regulators {
			compatible = "acme,pmic800-regulator";
			interrupt-parent = <&pmic>;
			interrupts = <0 IRQ_TYPE_LEVEL_HIGH>;
			interrupt-names = "buck1_oc";

			buck1: buck1 {
				regulator-name = "vdd_cpu";
				regulator-min-microvolt = <800000>;
				regulator-max-microvolt = <1350000>;
				regulator-boot-on;
				regulator-always-on;
			};

			buck2: buck2 {
				regulator-name = "vdd_gpu";
				regulator-min-microvolt = <800000>;
				regulator-max-microvolt = <1200000>;
			};
		};

		rtc {
			compatible = "acme,pmic800-rtc";
			interrupt-parent = <&pmic>;
			interrupts = <1 IRQ_TYPE_LEVEL_HIGH>;
		};

		onkey {
			compatible = "acme,pmic800-onkey";
			interrupt-parent = <&pmic>;
			interrupts = <2 IRQ_TYPE_LEVEL_HIGH>;
		};
	};
};
```

У вузлі `pmic@34` властивість `interrupt-controller` оголошує мікросхему локальним контролером переривань. Властивість `#interrupt-cells = <2>` визначає, що кожне дочірнє переривання задається двома числами: номером апаратної події в таблиці `acme_irqs` (0 — BUCK1_OC, 1 — RTC_ALARM, 2 — PWRKEY) та типом спрацьовування (фронт/рівень).

## 6. Аналіз типових пасток реалізації

Під час проектування подібних багаторівневих систем інженери часто стикаються з трьома критичними пастками:

1. **Контекст блокування Regmap:** Оскільки фізичний транспорт I2C виконує операції читання/запису, що можуть засинати (`might_sleep()`), внутрішній замок `regmap` ініціалізується як `struct mutex`. Спроба викликати `regmap_read()` або `regmap_update_bits()` із атомарного контексту або спинового замка (`spinlock`) призведе до паніки ядра з повідомленням `BUG: scheduling while atomic`. Якщо доступ із переривання верхньої половини дійсно необхідний, використовують безблокувальний доступ або переносять усю роботу у нижню половину (`threaded_irq` чи `workqueue`).
2. **Помилка отримання батьківського Regmap:** Якщо дочірній пристрій є онуком (наприклад, підвузол у складній ієрархії вузлів Device Tree), прямий виклик `dev_get_regmap(dev->parent, NULL)` поверне `NULL`, оскільки безпосередній батько не має асоційованого екземпляра `regmap`. Надійні дочірні драйвери виконують рекурсивний пошук по ланцюжку батьківських вузлів `dev->parent`, доки не знайдуть кореневий пристрій із дійсним дескриптором мапи регістрів.
3. **Порядок вивільнення ресурсів та Use-After-Free:** Завдяки використанню `devm_`-функцій (`devm_regmap_init_i2c`, `devm_regmap_add_irq_chip`, `devm_mfd_add_devices`), ядро автоматично вивільняє ресурси у строго зворотному порядку під час вивантаження модуля або помилки в середині `probe()`. Якщо ж розробник змішує ручний виклик `mfd_remove_devices()` та автоматичні `devm_`-деструктори, дочірні пристрої можуть спробувати звернутися до карти регістрів або домену переривань, які вже були знищені батьківським драйвером.
