static int acme_probe_legacy(struct platform_device *pdev)
{
	struct acme_chip *chip;
	struct resource *res;
	int ret;

	chip = kzalloc(sizeof(*chip), GFP_KERNEL);
	if (!chip)
		return -ENOMEM;

	res = platform_get_resource(pdev, IORESOURCE_MEM, 0);
	if (!res) {
		ret = -EINVAL;
		goto err_free_mem;
	}

	chip->regs = ioremap(res->start, resource_size(res));
	if (!chip->regs) {
		ret = -ENOMEM;
		goto err_free_mem;
	}

	chip->clk = clk_get(&pdev->dev, "core");
	if (IS_ERR(chip->clk)) {
		ret = PTR_ERR(chip->clk);
		goto err_unmap;
	}

	ret = clk_prepare_enable(chip->clk);
	if (ret)
		goto err_put_clk;

	chip->irq = platform_get_irq(pdev, 0);
	if (chip->irq < 0) {
		ret = chip->irq;
		goto err_disable_clk;
	}

	ret = request_threaded_irq(chip->irq, NULL, acme_irq_thread,
	                           IRQF_ONESHOT, "acme", chip);
	if (ret)
		goto err_disable_clk;

	return 0;

err_disable_clk:
	clk_disable_unprepare(chip->clk);
err_put_clk:
	clk_put(chip->clk);
err_unmap:
	iounmap(chip->regs);
err_free_mem:
	kfree(chip);
	return ret;
}
