// SPDX-License-Identifier: GPL-2.0
#include <linux/module.h>
#include <linux/platform_device.h>
#include <linux/property.h>
#include <linux/err.h>

#define FAKE_BASE 0x40000000UL
#define FAKE_SIZE 0x100
#define FAKE_IRQ  11

static struct platform_device *fake;

static const struct resource fake_res[] = {
        DEFINE_RES_MEM(FAKE_BASE, FAKE_SIZE),
        DEFINE_RES_IRQ(FAKE_IRQ),
};

static const struct property_entry fake_props[] = {
        PROPERTY_ENTRY_U32("clock-frequency", 24000000),
        { }
};

static int __init fake_init(void)
{
        struct platform_device_info info = {
                .name       = "myuart",
                .id         = 0,
                .res        = fake_res,
                .num_res    = ARRAY_SIZE(fake_res),
                .properties = fake_props,
        };

        fake = platform_device_register_full(&info);
        return PTR_ERR_OR_ZERO(fake);
}

static void __exit fake_exit(void)
{
        platform_device_unregister(fake);
}

module_init(fake_init);
module_exit(fake_exit);
MODULE_DESCRIPTION("Підроблений платформний пристрій для дослідів");
MODULE_LICENSE("GPL");
