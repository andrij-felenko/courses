#include <linux/module.h>
#include <linux/init.h>
#include <linux/platform_device.h>
#include <linux/gpio/consumer.h>

struct my_driver_priv {
    struct gpio_desc *reset_gpio;
    struct gpio_desc *status_led;
};

static int my_driver_probe(struct platform_device *pdev)
{
    struct device *dev = &pdev->dev;
    struct my_driver_priv *priv;

    priv = devm_kzalloc(dev, sizeof(*priv), GFP_KERNEL);
    if (!priv)
        return -ENOMEM;

    /*
     * Отримання лінії "reset", описаної в Device Tree як "reset-gpios".
     * Прапорець GPIOD_OUT_LOW атомарно конфігурує напрямок на вихід
     * і встановлює ЛОГІЧНИЙ НУЛЬ ще під час ініціалізації.
     */
    priv->reset_gpio = devm_gpiod_get(dev, "reset", GPIOD_OUT_LOW);
    if (IS_ERR(priv->reset_gpio)) {
        dev_err(dev, "Помилка отримання GPIO reset: %ld\n", PTR_ERR(priv->reset_gpio));
        return PTR_ERR(priv->reset_gpio);
    }

    /* Атомарне встановлення логічної одиниці (активація) */
    gpiod_set_value(priv->reset_gpio, 1);

    platform_set_drvdata(pdev, priv);
    return 0;
}
