static int acme_probe(struct platform_device *pdev)
{
	struct resource *res;
	struct acme *a;
	int ret;

	a = kzalloc(sizeof(*a), GFP_KERNEL);
	if (!a)
		return -ENOMEM;

	res = platform_get_resource(pdev, IORESOURCE_MEM, 0);
	if (!res) {
		ret = -EINVAL;
		goto err_free;
	}

	a->regs = ioremap(res->start, resource_size(res));
	if (!a->regs) {
		ret = -ENOMEM;
		goto err_free;
	}

	a->clk = clk_get(&pdev->dev, NULL);
	if (IS_ERR(a->clk)) {
		ret = PTR_ERR(a->clk);
		goto err_unmap;
	}

	ret = clk_prepare_enable(a->clk);
	if (ret)
		goto err_put_clk;

	a->irq = platform_get_irq(pdev, 0);
	if (a->irq < 0) {
		ret = a->irq;
		goto err_disable_clk;
	}

	ret = request_irq(a->irq, acme_isr, 0, "acme", a);
	if (ret)
		goto err_disable_clk;

	a->hwmon = hwmon_device_register_with_info(&pdev->dev, "acme", a,
						   &acme_chip_info, NULL);
	if (IS_ERR(a->hwmon)) {
		ret = PTR_ERR(a->hwmon);
		goto err_free_irq;
	}

	platform_set_drvdata(pdev, a);
	return 0;

err_free_irq:
	free_irq(a->irq, a);
err_disable_clk:
	clk_disable_unprepare(a->clk);
err_put_clk:
	clk_put(a->clk);
err_unmap:
	iounmap(a->regs);
err_free:
	kfree(a);
	return ret;
}
