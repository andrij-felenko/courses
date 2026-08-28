/* ── споживач ────────────────────────────────────────────────────────────── */

static int demo_consumer_runtime_suspend(struct device *dev)
{
	dev_info(dev, "runtime_suspend: контекст збережено\n");
	return 0;
}

static int demo_consumer_runtime_resume(struct device *dev)
{
	dev_info(dev, "runtime_resume: живлення вже є, відновлюю регістри\n");
	return 0;
}

static const struct dev_pm_ops demo_consumer_pm_ops = {
	RUNTIME_PM_OPS(demo_consumer_runtime_suspend,
		       demo_consumer_runtime_resume, NULL)
};

/* НАВМИСНО неправильно: «читання регістра» без заявки на живлення */
static ssize_t raw_read_show(struct device *dev,
			     struct device_attribute *attr, char *buf)
{
	bool live = demo_domains[DEMO_PD_DISPLAY].powered;

	return sysfs_emit(buf, "регіон %s: читання %s\n",
			  live ? "живий" : "знеструмлений",
			  live ? "пройшло б" : "підвісило б шину");
}
static DEVICE_ATTR_RO(raw_read);

static struct attribute *demo_consumer_attrs[] = {
	&dev_attr_raw_read.attr,
	NULL,
};
ATTRIBUTE_GROUPS(demo_consumer);

static int demo_consumer_probe(struct platform_device *pdev)
{
	struct device *dev = &pdev->dev;
	int ret;

	pm_runtime_set_autosuspend_delay(dev, 500);
	pm_runtime_use_autosuspend(dev);
	pm_runtime_enable(dev);

	ret = pm_runtime_resume_and_get(dev);   /* тільки після цього рядка
						   можна чіпати залізо */
	if (ret)
		goto err_disable;

	dev_info(dev, "ініціалізація заліза\n");

	/* завести файл power/pm_qos_resume_latency_us; поки без обмеження */
	dev_pm_qos_expose_latency_limit(dev, PM_QOS_RESUME_LATENCY_NO_CONSTRAINT);

	pm_runtime_put_autosuspend(dev);
	return 0;

err_disable:
	pm_runtime_disable(dev);
	pm_runtime_dont_use_autosuspend(dev);
	return ret;
}

static void demo_consumer_remove(struct platform_device *pdev)
{
	struct device *dev = &pdev->dev;

	dev_pm_qos_hide_latency_limit(dev);
	pm_runtime_get_sync(dev);               /* розбудити, поки облік діє */
	pm_runtime_disable(dev);
	pm_runtime_dont_use_autosuspend(dev);
	pm_runtime_put_noidle(dev);
}

static const struct of_device_id demo_consumer_match[] = {
	{ .compatible = "demo,pd-consumer" },
	{ }
};
MODULE_DEVICE_TABLE(of, demo_consumer_match);

static struct platform_driver demo_consumer_driver = {
	.probe	= demo_consumer_probe,
	.remove	= demo_consumer_remove,
	.driver	= {
		.name		= "demo-pd-consumer",
		.of_match_table	= demo_consumer_match,
		.pm		= pm_ptr(&demo_consumer_pm_ops),
		.dev_groups	= demo_consumer_groups,
	},
};

/* ── постачальник реєструється першим ────────────────────────────────────── */

static int __init demo_genpd_init(void)
{
	int ret;

	ret = platform_driver_register(&demo_pd_driver);
	if (ret)
		return ret;

	ret = platform_driver_register(&demo_consumer_driver);
	if (ret)
		platform_driver_unregister(&demo_pd_driver);
	return ret;
}

static void __exit demo_genpd_exit(void)
{
	platform_driver_unregister(&demo_consumer_driver);
	platform_driver_unregister(&demo_pd_driver);
}

module_init(demo_genpd_init);
module_exit(demo_genpd_exit);

MODULE_DESCRIPTION("Two genpd domains, a subdomain and a consumer on it");
MODULE_LICENSE("GPL");
