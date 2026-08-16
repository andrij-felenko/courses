# ⚙️ Приклад драйвера: робота з регулятором

Коли ми розробляємо драйвер для пристрою (наприклад, сенсора чи дисплея), нам потрібно гарантувати, що він отримає живлення перед початком будь-якої взаємодії на шині (I2C/SPI). Це робиться через API підсистеми регуляторів.

У цьому прикладі показано мінімальний шаблон драйвера: він запитує регулятор, встановлює потрібну робочу напругу, вмикає його, та вимикає при вивантаженні модуля.

```c
#include <linux/module.h>
#include <linux/platform_device.h>
#include <linux/regulator/consumer.h>

struct my_sensor_data {
    struct regulator *vdd_supply;
};

static int my_sensor_probe(struct platform_device *pdev)
{
    struct my_sensor_data *data;
    int ret;

    data = devm_kzalloc(&pdev->dev, sizeof(*data), GFP_KERNEL);
    if (!data)
        return -ENOMEM;

    /* 1. Запитуємо регулятор з ім'ям "vdd" (прив'язка описується у Device Tree).
     * Використовуємо devm_* версію, щоб ядро саме звільнило ресурс. */
    data->vdd_supply = devm_regulator_get(&pdev->dev, "vdd");
    if (IS_ERR(data->vdd_supply)) {
        dev_err(&pdev->dev, "Не вдалося знайти регулятор VDD\n");
        return PTR_ERR(data->vdd_supply);
    }

    /* 2. Запитуємо зміну напруги (мінімум 3.0V, максимум 3.3V).
     * Якщо інший пристрій на цій же лінії вимагає щонайменше 3.3V, 
     * фреймворк виставить 3.3V — найнижчу напругу, що влаштує всіх. */
    ret = regulator_set_voltage(data->vdd_supply, 3000000, 3300000);
    if (ret) {
        dev_err(&pdev->dev, "Помилка встановлення напруги: %d\n", ret);
        return ret;
    }

    /* 3. Вмикаємо живлення. */
    ret = regulator_enable(data->vdd_supply);
    if (ret) {
        dev_err(&pdev->dev, "Не вдалося увімкнути живлення сенсора\n");
        return ret;
    }

    dev_info(&pdev->dev, "Сенсор ініціалізовано, живлення увімкнено\n");
    platform_set_drvdata(pdev, data);
    return 0;
}

static int my_sensor_remove(struct platform_device *pdev)
{
    struct my_sensor_data *data = platform_get_drvdata(pdev);

    /* 4. Вимикаємо живлення при вивантаженні драйвера.
     * Якщо інші пристрої ще використовують цей регулятор, 
     * він фізично залишиться увімкненим, доки вони не звільнять його. */
    regulator_disable(data->vdd_supply);
    dev_info(&pdev->dev, "Живлення сенсора вимкнено\n");

    return 0;
}

static struct platform_driver my_sensor_driver = {
    .probe = my_sensor_probe,
    .remove = my_sensor_remove,
    .driver = {
        .name = "my_sensor",
    },
};
module_platform_driver(my_sensor_driver);

MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("Приклад використання Regulator Framework");
```

Одне застереження щодо версій ядра: до 6.10 включно поле `remove` у `struct platform_driver` мало підпис `int (*remove)(struct platform_device *)` — саме так, як у прикладі вище. Від 6.11 воно повертає `void`: код помилки з вивантаження драйвера ядро все одно ніде не обробляло. Тіло функції лишається тим самим, зникає лише `return 0;`.
