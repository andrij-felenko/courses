// SPDX-License-Identifier: GPL-2.0
#include <linux/init.h>
#include <linux/module.h>

static int __init lab_init(void)
{
	pr_info("lab: модуль стартував\n");
	return 0;
}

static void __exit lab_exit(void)
{
	pr_info("lab: модуль пішов\n");
}

module_init(lab_init);
module_exit(lab_exit);
MODULE_LICENSE("GPL");
