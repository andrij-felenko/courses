// SPDX-License-Identifier: GPL-2.0
#include <linux/delay.h>
#include <linux/device.h>
#include <linux/module.h>
#include <linux/platform_device.h>
#include <linux/slab.h>
#include <linux/workqueue.h>

static bool zlamaty;
module_param(zlamaty, bool, 0444);
MODULE_PARM_DESC(zlamaty, "звільняти буфер руками в remove() — відтворити пастку");

/* ── власний ресурс довгим шляхом ──────────────────────────────────────── */

struct kanal {
	int nomer;              /* усе, що потрібне функції звільнення */
};

/* res — вказівник на ДАНІ вузла, не на його шапку. */
static void kanal_release(struct device *dev, void *res)
{
	struct kanal *k = res;

	dev_info(dev, "   <- закрив канал %d\n", k->nomer);
}

/* Ознака, за якою вузол шукають серед вузлів із тим самим release. */
static int kanal_match(struct device *dev, void *res, void *dani)
{
	struct kanal *k = res;

	return k->nomer == *(int *)dani;
}

static int kanal_vidkryty(struct device *dev, int nomer)
{
	struct kanal *k;

	k = devres_alloc(kanal_release, sizeof(*k), GFP_KERNEL);
	if (!k)
		return -ENOMEM;
	k->nomer = nomer;
	devres_add(dev, k);     /* аж ТУТ вузол лягає у список пристрою */

	dev_info(dev, "-> відкрив канал %d\n", nomer);
	return 0;
}

/* ── необоротна дія коротким шляхом ────────────────────────────────────── */

struct stend {
	struct device      *dev;
	struct delayed_work robota;
	u32                *bufer;
	unsigned long       obertiv;
};

static void stend_robota(struct work_struct *w)
{
	struct stend *s = container_of(to_delayed_work(w), struct stend, robota);

	s->bufer[0] = 0xA11CE;          /* саме цей запис і стане пострілом */
	s->obertiv++;
	schedule_delayed_work(&s->robota, msecs_to_jiffies(20));
}

static void stend_zupynyty(void *dani)
{
	struct stend *s = dani;

	cancel_delayed_work_sync(&s->robota);
	dev_info(s->dev, "   <- спинив роботу після %lu обертів\n", s->obertiv);
}

/* ── прив'язка ─────────────────────────────────────────────────────────── */

static int stend_probe(struct platform_device *pdev)
{
	struct device *dev = &pdev->dev;
	int shukanyy = 2;
	struct stend *s;
	struct kanal *k;
	int i, ret;

	s = devm_kzalloc(dev, sizeof(*s), GFP_KERNEL);          /* вузол 1 */
	if (!s)
		return -ENOMEM;
	s->dev = dev;
	platform_set_drvdata(pdev, s);

	for (i = 1; i <= 3; i++) {                              /* вузли 2–4 */
		ret = kanal_vidkryty(dev, i);
		if (ret)
			return ret;
	}

	if (zlamaty)                                            /* вузол 5 */
		s->bufer = kzalloc(64 * sizeof(*s->bufer), GFP_KERNEL);
	else
		s->bufer = devm_kzalloc(dev, 64 * sizeof(*s->bufer), GFP_KERNEL);
	if (!s->bufer)
		return -ENOMEM;

	/* Необоротна дія — і ОДРАЗУ ж її скасування (вузол 6). */
	INIT_DELAYED_WORK(&s->robota, stend_robota);
	schedule_delayed_work(&s->robota, msecs_to_jiffies(20));
	ret = devm_add_action_or_reset(dev, stend_zupynyty, s);
	if (ret)
		return ret;

	/* Дострокове зняття: знайти канал 2 і викинути вузол мовчки. */
	k = devres_find(dev, kanal_release, kanal_match, &shukanyy);
	dev_info(dev, "devres_find(2) -> %s\n", k ? "знайшов" : "нема");
	dev_info(dev, "devres_destroy(2) -> %d\n",
		 devres_destroy(dev, kanal_release, kanal_match, &shukanyy));

	return 0;
}

static void stend_remove(struct platform_device *pdev)
{
	struct stend *s = platform_get_drvdata(pdev);

	dev_info(&pdev->dev, "remove(): почав\n");
	if (zlamaty) {
		kfree(s->bufer);   /* у цей буфер пише робота, яка ще жива */
		msleep(100);       /* даємо їй кілька обертів, щоб не гадати */
	}
	dev_info(&pdev->dev, "remove(): вийшов, devres ще не чіпали\n");
}

static struct platform_driver stend_driver = {
	.driver = { .name = "devres-stend" },
	.probe  = stend_probe,
	.remove = stend_remove,
};

static struct platform_device *stend_pdev;

static int __init stend_init(void)
{
	int ret = platform_driver_register(&stend_driver);

	if (ret)
		return ret;

	stend_pdev = platform_device_register_simple("devres-stend",
						     PLATFORM_DEVID_NONE, NULL, 0);
	if (IS_ERR(stend_pdev)) {
		platform_driver_unregister(&stend_driver);
		return PTR_ERR(stend_pdev);
	}
	return 0;
}

static void __exit stend_exit(void)
{
	platform_device_unregister(stend_pdev);
	platform_driver_unregister(&stend_driver);
}

module_init(stend_init);
module_exit(stend_exit);
MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("Стенд: власний керований ресурс і порядок його звільнення");
