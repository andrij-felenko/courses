// SPDX-License-Identifier: GPL-2.0
#include <linux/module.h>
#include <linux/platform_device.h>
#include <linux/property.h>
#include <linux/io.h>

struct myuart {
        void __iomem *regs;
        int           irq;
        u32           rate;
};

static int myuart_probe(struct platform_device *pdev)
{
        struct device *dev = &pdev->dev;
        struct myuart *up;

        up = devm_kzalloc(dev, sizeof(*up), GFP_KERNEL);
        if (!up)
                return -ENOMEM;

        up->regs = devm_platform_ioremap_resource(pdev, 0);
        if (IS_ERR(up->regs))
                return PTR_ERR(up->regs);

        up->irq = platform_get_irq(pdev, 0);
        if (up->irq < 0)
                return up->irq;              /* сюди приходить і -EPROBE_DEFER */

        if (device_property_read_u32(dev, "clock-frequency", &up->rate))
                up->rate = 50000000;         /* властивості нема — усталене */

        platform_set_drvdata(pdev, up);
        dev_info(dev, "прив'язано: лінія %d, такт %u Гц, перше слово 0x%08x\n",
                 up->irq, up->rate, readl(up->regs));
        return 0;
}

static void myuart_remove(struct platform_device *pdev)
{
        struct myuart *up = platform_get_drvdata(pdev);

        dev_info(&pdev->dev, "від'єднано, такт був %u Гц\n", up->rate);
}

static const struct of_device_id myuart_of_match[] = {
        { .compatible = "acme,myuart-r1p2" },
        { }
};
MODULE_DEVICE_TABLE(of, myuart_of_match);

static struct platform_driver myuart_driver = {
        .probe  = myuart_probe,
        .remove = myuart_remove,
        .driver = {
                .name           = "myuart",
                .of_match_table = myuart_of_match,
        },
};
module_platform_driver(myuart_driver);

MODULE_DESCRIPTION("Навчальний платформний драйвер");
MODULE_LICENSE("GPL");
