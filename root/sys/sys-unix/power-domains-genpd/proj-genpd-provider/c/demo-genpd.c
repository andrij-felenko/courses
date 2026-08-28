// demo-genpd.c — два домени живлення, піддомен і споживач на ньому
#include <linux/module.h>
#include <linux/platform_device.h>
#include <linux/pm_domain.h>
#include <linux/pm_runtime.h>
#include <linux/pm_qos.h>
#include <linux/delay.h>
#include <linux/of.h>

/* ── «залізо»: кожен вимикач — це один прапорець ─────────────────────────── */

struct demo_domain {
	struct generic_pm_domain genpd;      /* мусить бути першим полем */
	bool			 powered;    /* замість біта в регістрі PMU */
};

enum { DEMO_PD_MEDIA, DEMO_PD_DISPLAY, DEMO_PD_COUNT };

static int demo_power_on(struct generic_pm_domain *genpd)
{
	struct demo_domain *d = container_of(genpd, struct demo_domain, genpd);

	usleep_range(800, 1200);             /* напруга усталюється */
	d->powered = true;
	pr_info("%s: power_on\n", genpd->name);
	return 0;
}

static int demo_power_off(struct generic_pm_domain *genpd)
{
	struct demo_domain *d = container_of(genpd, struct demo_domain, genpd);

	d->powered = false;
	pr_info("%s: power_off (стан %u)\n", genpd->name, genpd->state_idx);
	return 0;
}

#define DEMO_DOMAIN(nm) {					\
	.genpd = {						\
		.name	   = nm,				\
		.power_on  = demo_power_on,			\
		.power_off = demo_power_off,			\
	},							\
}

static struct demo_domain demo_domains[DEMO_PD_COUNT] = {
	[DEMO_PD_MEDIA]	  = DEMO_DOMAIN("pd-media"),
	[DEMO_PD_DISPLAY] = DEMO_DOMAIN("pd-display"),
};

static struct generic_pm_domain *demo_domain_ptrs[DEMO_PD_COUNT];

static struct genpd_onecell_data demo_onecell = {
	.domains     = demo_domain_ptrs,
	.num_domains = DEMO_PD_COUNT,
};

/* ── реєстрація: ініціалізувати → вкласти → аж тоді віддати назовні ──────── */

static int demo_pd_probe(struct platform_device *pdev)
{
	struct device *dev = &pdev->dev;
	int i, ret;

	for (i = 0; i < DEMO_PD_COUNT; i++) {
		demo_domain_ptrs[i] = &demo_domains[i].genpd;

		/* is_off = true — обіцянка про залізо: воно справді знеструмлене.
		   Заразом це знімає «тримати ввімкненим до ->sync_state».      */
		ret = pm_genpd_init(&demo_domains[i].genpd,
				    &simple_qos_governor, true);
		if (ret)
			goto err_undo;
	}

	ret = pm_genpd_add_subdomain(&demo_domains[DEMO_PD_MEDIA].genpd,
				     &demo_domains[DEMO_PD_DISPLAY].genpd);
	if (ret)
		goto err_undo;

	/* вкладеність зібрана — тепер споживач не застане півготового дерева */
	ret = of_genpd_add_provider_onecell(dev->of_node, &demo_onecell);
	if (ret)
		goto err_subdomain;

	dev_info(dev, "домени зареєстровано: pd-media ⊃ pd-display\n");
	return 0;

err_subdomain:
	pm_genpd_remove_subdomain(&demo_domains[DEMO_PD_MEDIA].genpd,
				  &demo_domains[DEMO_PD_DISPLAY].genpd);
err_undo:
	while (--i >= 0)
		pm_genpd_remove(&demo_domains[i].genpd);
	return ret;
}

static void demo_pd_remove(struct platform_device *pdev)
{
	int i;

	of_genpd_del_provider(pdev->dev.of_node);
	pm_genpd_remove_subdomain(&demo_domains[DEMO_PD_MEDIA].genpd,
				  &demo_domains[DEMO_PD_DISPLAY].genpd);
	for (i = 0; i < DEMO_PD_COUNT; i++)
		pm_genpd_remove(&demo_domains[i].genpd);
}

static const struct of_device_id demo_pd_match[] = {
	{ .compatible = "demo,pd-controller" },
	{ }
};
MODULE_DEVICE_TABLE(of, demo_pd_match);

static struct platform_driver demo_pd_driver = {
	.probe	= demo_pd_probe,
	.remove	= demo_pd_remove,
	.driver	= {
		.name		= "demo-pd-controller",
		.of_match_table	= demo_pd_match,
	},
};
