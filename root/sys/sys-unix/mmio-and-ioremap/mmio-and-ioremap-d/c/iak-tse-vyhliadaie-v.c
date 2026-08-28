#define REG_ID          0x000   /* лише читання: сигнатура блока */
#define REG_IRQ_CAUSE   0x00c   /* запис одиниці скидає біт */
#define REG_TXDESC_LO   0x010
#define REG_TXDESC_HI   0x014
#define REG_TX_KICK     0x018

struct myeth {
        void __iomem *regs;
        struct device *dev;
};

static int myeth_probe(struct platform_device *pdev)
{
        struct myeth *priv;

        priv = devm_kzalloc(&pdev->dev, sizeof(*priv), GFP_KERNEL);
        if (!priv)
                return -ENOMEM;
        priv->dev = &pdev->dev;

        /* займає діапазон у /proc/iomem, відображає його
           й вішає звільнення на знищення пристрою */
        priv->regs = devm_platform_ioremap_resource(pdev, 0);
        if (IS_ERR(priv->regs))
                return PTR_ERR(priv->regs);

        if (readl(priv->regs + REG_ID) != 0x4d594554)
                return dev_err_probe(&pdev->dev, -ENODEV,
                                     "за цією адресою не наш блок\n");

        platform_set_drvdata(pdev, priv);
        return 0;
}
