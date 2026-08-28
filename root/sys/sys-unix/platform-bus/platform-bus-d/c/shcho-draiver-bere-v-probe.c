static int myuart_probe(struct platform_device *pdev)
{
        struct myuart *up;
        int ret;

        up = devm_kzalloc(&pdev->dev, sizeof(*up), GFP_KERNEL);
        if (!up)
                return -ENOMEM;

        up->regs = devm_platform_ioremap_resource(pdev, 0);
        if (IS_ERR(up->regs))
                return PTR_ERR(up->regs);

        up->irq = platform_get_irq(pdev, 0);
        if (up->irq < 0)
                return up->irq;              /* сюди приходить і -EPROBE_DEFER */

        ret = devm_request_irq(&pdev->dev, up->irq, myuart_isr, 0,
                               dev_name(&pdev->dev), up);
        if (ret)
                return ret;

        platform_set_drvdata(pdev, up);
        dev_info(&pdev->dev, "порт готовий, лінія переривання %d\n", up->irq);
        return 0;
}

static const struct of_device_id myuart_of_match[] = {
        { .compatible = "acme,myuart-r1p2" },
        { }
};
MODULE_DEVICE_TABLE(of, myuart_of_match);

static struct platform_driver myuart_driver = {
        .probe  = myuart_probe,
        .driver = {
                .name           = "myuart",
                .of_match_table = myuart_of_match,
        },
};
module_platform_driver(myuart_driver);
