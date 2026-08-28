// pmlab.c — пристрій, у якому немає нічого, крім обліку живлення
#include <linux/module.h>
#include <linux/platform_device.h>
#include <linux/pm_runtime.h>
#include <linux/delay.h>
#include <linux/kstrtox.h>

#define PMLAB_RESUME_MS       40   /* «підняти напругу й відновити регістри» */
#define PMLAB_SUSPEND_MS      10   /* «зберегти контекст і зняти напругу»    */
#define PMLAB_AUTOSUSPEND_MS 500   /* витримка перед сном                    */

/* ── три зворотні виклики: замість заліза — журнал і чесна затримка ─────── */

static int pmlab_runtime_suspend(struct device *dev)
{
	dev_info(dev, "suspend: гашу живлення\n");
	msleep(PMLAB_SUSPEND_MS);
	return 0;
}

static int pmlab_runtime_resume(struct device *dev)
{
	dev_info(dev, "resume: подаю живлення\n");
	msleep(PMLAB_RESUME_MS);          /* тут живе ціна пробудження */
	return 0;
}

static int pmlab_runtime_idle(struct device *dev)
{
	dev_info(dev, "idle: лічильник щойно впав до нуля\n");
	return 0;                         /* 0 → ядро саме попросить присипляння */
}

static const struct dev_pm_ops pmlab_pm_ops = {
	RUNTIME_PM_OPS(pmlab_runtime_suspend, pmlab_runtime_resume,
		       pmlab_runtime_idle)
};

/* ── атрибут: запис числа = звернення до пристрою на стільки мілісекунд ─── */

static ssize_t poke_store(struct device *dev, struct device_attribute *attr,
			  const char *buf, size_t count)
{
	unsigned int ms;
	int ret;

	ret = kstrtouint(buf, 10, &ms);
	if (ret)
		return ret;
	if (ms > 2000)
		return -ERANGE;

	ret = pm_runtime_resume_and_get(dev);  /* +1; на невдачі не лишить +1 */
	if (ret)
		return ret;

	msleep(ms);                            /* «робота» з пристроєм */
	dev_info(dev, "poke: попрацював %u мс\n", ms);

	pm_runtime_put_autosuspend(dev);       /* −1 і, якщо нуль, — відлік */
	return count;
}
static DEVICE_ATTR_WO(poke);               /* права 0200: пише лише root */

static struct attribute *pmlab_attrs[] = {
	&dev_attr_poke.attr,
	NULL,
};
ATTRIBUTE_GROUPS(pmlab);

/* ── вмикання й вимикання обліку ────────────────────────────────────────── */

static int pmlab_probe(struct platform_device *pdev)
{
	struct device *dev = &pdev->dev;
	int ret;

	pm_runtime_set_active(dev);            /* правда: живлення вже подано */
	pm_runtime_set_autosuspend_delay(dev, PMLAB_AUTOSUSPEND_MS);
	pm_runtime_use_autosuspend(dev);
	pm_runtime_enable(dev);                /* відтепер помічники діють */

	ret = pm_runtime_resume_and_get(dev);  /* +1 на час ініціалізації */
	if (ret)
		goto err_disable;

	dev_info(dev, "готовий; затримка автосну %d мс\n", PMLAB_AUTOSUSPEND_MS);

	pm_runtime_put_autosuspend(dev);       /* −1: далі вирішує лічильник */
	return 0;

err_disable:                                   /* дзеркало до чотирьох рядків вище */
	pm_runtime_disable(dev);
	pm_runtime_dont_use_autosuspend(dev);
	pm_runtime_set_suspended(dev);
	return ret;
}

static void pmlab_remove(struct platform_device *pdev)
{
	struct device *dev = &pdev->dev;

	pm_runtime_get_sync(dev);              /* розбудити, щоб гасити свідомо */
	pm_runtime_disable(dev);               /* помічники більше не діють */
	pm_runtime_dont_use_autosuspend(dev);
	pm_runtime_set_suspended(dev);         /* облік лишаємо в стані «спить» */
	pm_runtime_put_noidle(dev);            /* −1 без спроби щось присипляти */
}

static struct platform_driver pmlab_driver = {
	.probe	= pmlab_probe,
	.remove	= pmlab_remove,
	.driver	= {
		.name		= "pmlab",
		.pm		= pm_ptr(&pmlab_pm_ops),
		.dev_groups	= pmlab_groups,  /* файл з'явиться при прив'язці */
	},
};

static struct platform_device *pmlab_pdev;

static int __init pmlab_init(void)
{
	int ret;

	ret = platform_driver_register(&pmlab_driver);
	if (ret)
		return ret;

	pmlab_pdev = platform_device_register_simple("pmlab", 0, NULL, 0);
	if (IS_ERR(pmlab_pdev)) {
		platform_driver_unregister(&pmlab_driver);
		return PTR_ERR(pmlab_pdev);
	}
	return 0;
}

static void __exit pmlab_exit(void)
{
	platform_device_unregister(pmlab_pdev);   /* → pmlab_remove */
	platform_driver_unregister(&pmlab_driver);
}

module_init(pmlab_init);
module_exit(pmlab_exit);

MODULE_DESCRIPTION("Runtime PM playground: a device made of accounting only");
MODULE_LICENSE("GPL");
