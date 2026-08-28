#include <linux/module.h>
#include <linux/init.h>
#include <linux/fs.h>
#include <linux/platform_device.h>
#include <linux/gpio/consumer.h>
#include <linux/interrupt.h>
#include <linux/delay.h>
#include <linux/slab.h>

#define DRIVER_NAME "acme_sensor_driver"

/* Приватна структура стану пристрою */
struct acme_sensor_dev {
    struct device *dev;
    struct gpio_desc *reset_gpio;
    struct gpio_desc *enable_gpio;
    struct gpio_desc *irq_gpio;
    int irq_num;
};

/* Обробник переривання лінії IRQ GPIO */
static irqreturn_t acme_sensor_irq_handler(int irq, void *dev_id)
{
    struct acme_sensor_dev *priv = dev_id;

    dev_info(priv->dev, "IRQ triggered on GPIO line! Sensor data ready.\n");
    return IRQ_HANDLED;
}

/* Функція ініціалізації пристрою (Probe) */
static int acme_sensor_probe(struct platform_device *pdev)
{
    struct device *dev = &pdev->dev;
    struct acme_sensor_dev *priv;
    int ret;

    dev_info(dev, "Probing ACME Sensor Device...\n");

    /* 1. Виділення пам'яті під приватну структуру пристрою через Devres */
    priv = devm_kzalloc(dev, sizeof(*priv), GFP_KERNEL);
    if (!priv)
        return -ENOMEM;

    priv->dev = dev;

    /* 2. Отримання обов'язкової лінії Reset (встановлюємо логічний 0 = неактивний) */
    priv->reset_gpio = devm_gpiod_get(dev, "reset", GPIOD_OUT_LOW);
    if (IS_ERR(priv->reset_gpio)) {
        ret = PTR_ERR(priv->reset_gpio);
        if (ret != -EPROBE_DEFER)
            dev_err(dev, "Failed to get 'reset' GPIO: %d\n", ret);
        return ret;
    }

    /* 3. Отримання опціональної лінії Enable */
    priv->enable_gpio = devm_gpiod_get_optional(dev, "enable", GPIOD_OUT_HIGH);
    if (IS_ERR(priv->enable_gpio)) {
        ret = PTR_ERR(priv->enable_gpio);
        if (ret != -EPROBE_DEFER)
            dev_err(dev, "Failed to get optional 'enable' GPIO: %d\n", ret);
        return ret;
    }

    /* 4. Отримання вхідної лінії переривання IRQ */
    priv->irq_gpio = devm_gpiod_get(dev, "irq", GPIOD_IN);
    if (IS_ERR(priv->irq_gpio)) {
        ret = PTR_ERR(priv->irq_gpio);
        if (ret != -EPROBE_DEFER)
            dev_err(dev, "Failed to get 'irq' GPIO: %d\n", ret);
        return ret;
    }

    /* 5. Перетворення дескриптора GPIO у номер системного переривання */
    priv->irq_num = gpiod_to_irq(priv->irq_gpio);
    if (priv->irq_num < 0) {
        dev_err(dev, "Failed to map IRQ GPIO to system IRQ: %d\n", priv->irq_num);
        return priv->irq_num;
    }

    /* 6. Реєстрація потокового обробника переривання через Devres */
    ret = devm_request_threaded_irq(dev, priv->irq_num, NULL,
                                   acme_sensor_irq_handler,
                                   IRQF_TRIGGER_RISING | IRQF_ONESHOT,
                                   "acme_sensor_irq", priv);
    if (ret) {
        dev_err(dev, "Failed to request IRQ %d: %d\n", priv->irq_num, ret);
        return ret;
    }

    /* 7. Виконання апаратного скидання датчика (Pulse Reset) */
    dev_info(dev, "Asserting hardware Reset (Logical 1)...\n");
    gpiod_set_value(priv->reset_gpio, 1); /* Активація скидання */
    msleep(20);                           /* Тимчасова затримка 20 мс */
    
    dev_info(dev, "Deasserting hardware Reset (Logical 0)...\n");
    gpiod_set_value(priv->reset_gpio, 0); /* Зняття скидання */

    platform_set_drvdata(pdev, priv);
    dev_info(dev, "ACME Sensor probed successfully! Assigned IRQ: %d\n", priv->irq_num);

    return 0;
}

/* Опис відповідності Дерева пристроїв (Device Tree Matching) */
static const struct of_device_id acme_sensor_of_match[] = {
    { .compatible = "acme,sensor" },
    { /* sentinel */ }
};
MODULE_DEVICE_TABLE(of, acme_sensor_of_match);

static struct platform_driver acme_sensor_driver = {
    .probe = acme_sensor_probe,
    .driver = {
        .name = DRIVER_NAME,
        .of_match_table = acme_sensor_of_match,
    },
};

module_platform_driver(acme_sensor_driver);

MODULE_LICENSE("GPL v2");
MODULE_AUTHOR("Antigravity Engineer");
MODULE_DESCRIPTION("Example driver demonstrating Kernel gpiod Consumer API");
