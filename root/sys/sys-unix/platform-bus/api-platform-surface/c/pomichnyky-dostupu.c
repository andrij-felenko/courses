static int acme_probe(struct platform_device *pdev)
{
        struct acme *a;
        int irq, ret;

        a = devm_kzalloc(&pdev->dev, sizeof(*a), GFP_KERNEL);
        if (!a)
                return -ENOMEM;

        a->regs = devm_platform_ioremap_resource_byname(pdev, "cfg");
        if (IS_ERR(a->regs))
                return PTR_ERR(a->regs);

        irq = platform_get_irq_byname(pdev, "rx");
        if (irq < 0)
                return irq;

        ret = devm_request_irq(&pdev->dev, irq, acme_isr, 0,
                               dev_name(&pdev->dev), a);
        if (ret)
                return ret;

        platform_set_drvdata(pdev, a);
        return 0;
}
