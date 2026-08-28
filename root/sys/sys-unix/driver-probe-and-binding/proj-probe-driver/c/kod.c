// SPDX-License-Identifier: GPL-2.0
#include <linux/module.h>
#include <linux/platform_device.h>

static struct platform_device *datchyk, *dzherelo;

static int __init plata_init(void)
{
	datchyk = platform_device_register_simple("termodatchyk",
						  PLATFORM_DEVID_NONE, NULL, 0);
	if (IS_ERR(datchyk))
		return PTR_ERR(datchyk);

	dzherelo = platform_device_register_simple("dzherelo",
						   PLATFORM_DEVID_NONE, NULL, 0);
	if (IS_ERR(dzherelo)) {
		platform_device_unregister(datchyk);
		return PTR_ERR(dzherelo);
	}
	return 0;
}

static void __exit plata_exit(void)
{
	platform_device_unregister(dzherelo);
	platform_device_unregister(datchyk);
}

module_init(plata_init);
module_exit(plata_exit);
MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("Стенд: два вигадані пристрої на шині platform");
