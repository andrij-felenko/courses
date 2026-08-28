static int legacy_probe(struct platform_device *pdev)
{
	/* 1. Пам'ять */
	priv = kzalloc(sizeof(*priv), GFP_KERNEL);
	if (!priv)
		return -ENOMEM;

	/* 2. MMIO */
	res = platform_get_resource(pdev, IORESOURCE_MEM, 0);
	if (!res) {
		ret = -EINVAL;
		goto err_free_priv;
	}
	priv->regs = ioremap(res->start, resource_size(res));
	if (!priv->regs) {
		ret = -ENOMEM;
		goto err_free_priv;
	}

	/* 3. Тактування */
	priv->clk = clk_get(&pdev->dev, NULL);
	if (IS_ERR(priv->clk)) {
		ret = PTR_ERR(priv->clk);
		goto err_unmap;
	}

	/* 4. Переривання */
	ret = request_irq(priv->irq, isr_handler, 0, "legacy", priv);
	if (ret)
		goto err_put_clk;

	return 0;

err_put_clk:
	clk_put(priv->clk);
err_unmap:
	iounmap(priv->regs);
err_free_priv:
	kfree(priv);
	return ret;
}
