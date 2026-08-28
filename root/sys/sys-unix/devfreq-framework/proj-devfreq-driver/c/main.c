#include <linux/module.h>
#include <linux/platform_device.h>
#include <linux/devfreq.h>
#include <linux/pm_opp.h>
#include <linux/clk.h>
#include <linux/io.h>
#include <linux/slab.h>

#define REG_BUS_TOTAL_CYCLES   0x00
#define REG_BUS_BUSY_CYCLES    0x04
#define REG_BUS_CTRL           0x08
#define BUS_CTRL_RESET_COUNTERS BIT(0)

struct sample_bus_devfreq {
    struct device *dev;
    void __iomem *regs;
    struct clk *clk;
    struct devfreq *df;
    struct devfreq_dev_profile profile;
    struct mutex lock;
};

/* Зчитування апаратних метрик навантаження */
static int sample_bus_get_dev_status(struct device *dev,
                                     struct devfreq_dev_status *stat)
{
    struct sample_bus_devfreq *priv = dev_get_drvdata(dev);
    u32 total_cycles, busy_cycles;

    mutex_lock(&priv->lock);

    /* Зчитуємо 32-бітні лічильники апаратних циклів */
    total_cycles = readl_relaxed(priv->regs + REG_BUS_TOTAL_CYCLES);
    busy_cycles  = readl_relaxed(priv->regs + REG_BUS_BUSY_CYCLES);

    /* Скидаємо апаратні лічильники для наступного інтервалу вимірювання */
    writel_relaxed(BUS_CTRL_RESET_COUNTERS, priv->regs + REG_BUS_CTRL);

    stat->current_frequency = clk_get_rate(priv->clk);
    stat->total_time = total_cycles;
    stat->busy_time  = busy_cycles;
    stat->private_data = NULL;

    mutex_unlock(&priv->lock);
    return 0;
}

/* Встановлення цільової частоти, запрошеної регулятором */
static int sample_bus_target(struct device *dev, unsigned long *freq, u32 flags)
{
    struct dev_pm_opp *opp;
    int ret;

    /* Шукаємо найближчу доступну точку OPP, що задовольняє запит */
    opp = devfreq_recommended_opp(dev, freq, flags);
    if (IS_ERR(opp)) {
        dev_err(dev, "Не знайдено валідної точки OPP для частоти %lu Гц\n", *freq);
        return PTR_ERR(opp);
    }
    dev_pm_opp_put(opp);

    /* Застосовуємо зміну частоти та напруги через OPP API */
    ret = dev_pm_opp_set_rate(dev, *freq);
    if (ret) {
        dev_err(dev, "Помилка встановлення частоти %lu Гц: %d\n", *freq, ret);
        return ret;
    }

    return 0;
}

static int sample_bus_probe(struct platform_device *pdev)
{
    struct device *dev = &pdev->dev;
    struct sample_bus_devfreq *priv;
    int ret;

    priv = devm_kzalloc(dev, sizeof(*priv), GFP_KERNEL);
    if (!priv)
        return -ENOMEM;

    priv->dev = dev;
    mutex_init(&priv->lock);

    priv->regs = devm_platform_ioremap_resource(pdev, 0);
    if (IS_ERR(priv->regs))
        return PTR_ERR(priv->regs);

    priv->clk = devm_clk_get(dev, "bus_clk");
    if (IS_ERR(priv->clk))
        return dev_err_probe(dev, PTR_ERR(priv->clk), "Не вдалося отримати тактовий сигнал\n");

    /* Ініціалізація таблиці OPP з Device Tree */
    ret = devm_pm_opp_of_add_table(dev);
    if (ret)
        return dev_err_probe(dev, ret, "Помилка парсингу OPP таблиці з DT\n");

    /* Конфігурація регулятора напруги через OPP Framework */
    ret = devm_pm_opp_set_regulators(dev, (const char *[]){ "bus" }, 1);
    if (ret)
        return dev_err_probe(dev, ret, "Помилка реєстрації регулятора живлення\n");

    /* Заповнення структури профілю devfreq */
    priv->profile.polling_ms = 50; /* Інтервал опитування за замовчуванням: 50 мс */
    priv->profile.target = sample_bus_target;
    priv->profile.get_dev_status = sample_bus_get_dev_status;
    priv->profile.initial_freq = clk_get_rate(priv->clk);

    platform_set_drvdata(pdev, priv);

    /* Реєстрація керованого devfreq-пристрою з регулятором simple_ondemand */
    priv->df = devm_devfreq_add_device(dev, &priv->profile,
                                       DEVFREQ_GOV_SIMPLE_ONDEMAND, NULL);
    if (IS_ERR(priv->df))
        return dev_err_probe(dev, PTR_ERR(priv->df), "Помилка реєстрації devfreq\n");

    dev_info(dev, "Драйвер devfreq шини успішно зареєстровано, початкова частота: %lu Гц\n",
             priv->profile.initial_freq);
    return 0;
}

static const struct of_device_id sample_bus_of_match[] = {
    { .compatible = "vendor,sample-bus-controller" },
    { /* кінець списку */ }
};
MODULE_DEVICE_TABLE(of, sample_bus_of_match);

static struct platform_driver sample_bus_driver = {
    .probe = sample_bus_probe,
    .driver = {
        .name = "sample-bus-devfreq",
        .of_match_table = sample_bus_of_match,
    },
};
module_platform_driver(sample_bus_driver);

MODULE_AUTHOR("Antigravity Devfreq Team");
MODULE_DESCRIPTION("Devfreq драйвер для контролера системної шини пам'яті");
MODULE_LICENSE("GPL");
