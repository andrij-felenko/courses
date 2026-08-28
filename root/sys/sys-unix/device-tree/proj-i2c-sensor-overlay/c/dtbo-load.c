// dtbo-load.c — накласти .dtbo з /lib/firmware на живе дерево пристроїв
#include <linux/module.h>
#include <linux/firmware.h>
#include <linux/of.h>
#include <linux/platform_device.h>

static char *dtbo = "tmp102-sensor.dtbo";
module_param(dtbo, charp, 0444);
MODULE_PARM_DESC(dtbo, "ім'я файлу накладки в /lib/firmware");

static struct platform_device *anchor;
static int ovcs_id;

static int __init dtbo_load_init(void)
{
	const struct firmware *fw;
	int ret;

	/* request_firmware потребує справжнього пристрою як власника запиту */
	anchor = platform_device_register_simple("dtbo-load", -1, NULL, 0);
	if (IS_ERR(anchor))
		return PTR_ERR(anchor);

	ret = request_firmware(&fw, dtbo, &anchor->dev);
	if (ret) {
		dev_err(&anchor->dev, "нема %s у /lib/firmware: %d\n", dtbo, ret);
		goto err;
	}

	/* NULL як ціль — накладати на все дерево, а не на піддерево */
	ret = of_overlay_fdt_apply(fw->data, fw->size, &ovcs_id, NULL);
	release_firmware(fw);
	if (ret) {
		dev_err(&anchor->dev, "накладка не лягла: %d\n", ret);
		goto err;
	}
	return 0;

err:
	platform_device_unregister(anchor);
	return ret;
}

static void __exit dtbo_load_exit(void)
{
	of_overlay_remove(&ovcs_id);
	platform_device_unregister(anchor);
}

module_init(dtbo_load_init);
module_exit(dtbo_load_exit);
MODULE_LICENSE("GPL");
