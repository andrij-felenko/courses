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
