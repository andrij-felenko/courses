// SPDX-License-Identifier: GPL-2.0
#include <linux/module.h>
#include <linux/platform_device.h>

static int dzherelo_probe(struct platform_device *pdev)
{
	dev_info(&pdev->dev, "джерело готове\n");
	return 0;
}

static struct platform_driver dzherelo_driver = {
	.driver = { .name = "dzherelo" },
	.probe  = dzherelo_probe,
};
module_platform_driver(dzherelo_driver);

MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("Порожній постачальник, якого чекає термодатчик");
