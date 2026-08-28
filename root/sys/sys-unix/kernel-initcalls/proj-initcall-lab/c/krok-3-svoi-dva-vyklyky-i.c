// SPDX-License-Identifier: GPL-2.0
#include <linux/errno.h>
#include <linux/init.h>
#include <linux/jiffies.h>
#include <linux/printk.h>

static int __init lab_core(void)
{
	pr_info("initlab: core, jiffies=%lu\n", jiffies);
	return 0;
}
core_initcall(lab_core);

static int __init lab_late(void)
{
	pr_info("initlab: late, jiffies=%lu\n", jiffies);
	return -EIO;   /* навмисна помилка — подивимося, чи вона щось спинить */
}
late_initcall(lab_late);
