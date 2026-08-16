# Proj Clk Driver Example

### Приклад: Увімкнення тактування у драйвері пристрою

Драйвер периферійного пристрою (наприклад, I2C контролера) зазвичай не знає, як саме формується його тактова частота. Він лише отримує вказівник на `struct clk` і вмикає його під час ініціалізації:

```c
#include <linux/clk.h>
#include <linux/err.h>
#include <linux/platform_device.h>

struct my_device_data {
    struct clk *clk;
    void __iomem *base;
};

static int my_device_probe(struct platform_device *pdev)
{
    struct my_device_data *data;
    int ret;

    data = devm_kzalloc(&pdev->dev, sizeof(*data), GFP_KERNEL);
    if (!data)
        return -ENOMEM;

    /* 1. Отримуємо тактовий сигнал з Device Tree за назвою "bus" */
    data->clk = devm_clk_get(&pdev->dev, "bus");
    if (IS_ERR(data->clk)) {
        dev_err(&pdev->dev, "failed to get clock\n");
        return PTR_ERR(data->clk);
    }

    /* 2. Одночасно готуємо (prepare) та вмикаємо (enable) тактування */
    ret = clk_prepare_enable(data->clk);
    if (ret) {
        dev_err(&pdev->dev, "failed to enable clock\n");
        return ret;
    }

    /* Тепер на контролер подається тактовий сигнал, можна звертатися до його регістрів */
    
    // ... ініціалізація апаратури ...

    platform_set_drvdata(pdev, data);
    return 0;
}

static int my_device_remove(struct platform_device *pdev)
{
    struct my_device_data *data = platform_get_drvdata(pdev);

    /* Вимикаємо тактування при вивантаженні драйвера для збереження енергії */
    clk_disable_unprepare(data->clk);

    return 0;
}
```

**Чому `devm_`?** 
Префікс `devm_` (Device Resource Management) означає, що ядро автоматично вивільнить ресурс (у цьому випадку — викличе `clk_put()`), коли пристрій буде видалено або якщо `probe` завершиться помилкою. Це позбавляє від необхідності писати складний код очищення в секціях `goto error`. Зверніть увагу, що `clk_prepare_enable` треба відкочувати вручну через `clk_disable_unprepare`. І ще про сигнатуру: у ядрах до 6.11 метод `remove` платформного драйвера повертав `int` (повернене значення ядро однаково ігнорувало), а з 6.11 він оголошений як `void` — у свіжому дереві цей метод пишуть `static void my_device_remove(struct platform_device *pdev)` без `return`.
