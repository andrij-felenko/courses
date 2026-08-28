static void acme_disable_hardware_action(void *data)
{
	struct acme_chip *chip = data;

	/* Апаратне вимкнення вимірювань */
	writel(0, chip->regs + ACME_REG_ENABLE);
}

static int acme_probe(struct platform_device *pdev)
{
	/* ... ініціалізація пам'яті, MMIO та тактів ... */

	/* Вмикаємо залізо */
	writel(ACME_ENABLE_BIT, chip->regs + ACME_REG_ENABLE);

	/* Реєструємо автоматичне вимкнення заліза під час демонтажу */
	ret = devm_add_action_or_reset(&pdev->dev, acme_disable_hardware_action, chip);
	if (ret)
		return ret;

	return 0;
}
