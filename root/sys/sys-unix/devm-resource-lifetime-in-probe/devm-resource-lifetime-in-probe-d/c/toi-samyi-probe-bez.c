static int acme_probe(struct platform_device *pdev)
{
	struct device *dev = &pdev->dev;
	struct device *hwmon;
	struct acme *a;
	int ret;

	a = devm_kzalloc(dev, sizeof(*a), GFP_KERNEL);
	if (!a)
		return -ENOMEM;

	a->regs = devm_platform_ioremap_resource(pdev, 0);
	if (IS_ERR(a->regs))
		return PTR_ERR(a->regs);

	a->clk = devm_clk_get_enabled(dev, NULL);
	if (IS_ERR(a->clk))
		return PTR_ERR(a->clk);

	a->irq = platform_get_irq(pdev, 0);
	if (a->irq < 0)
		return a->irq;

	ret = devm_request_irq(dev, a->irq, acme_isr, 0, "acme", a);
	if (ret)
		return ret;

	hwmon = devm_hwmon_device_register_with_info(dev, "acme", a,
						     &acme_chip_info, NULL);
	return PTR_ERR_OR_ZERO(hwmon);
}
