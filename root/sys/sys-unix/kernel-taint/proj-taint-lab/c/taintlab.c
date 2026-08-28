/* taintlab.c — піддослідний модуль: кожна пляма вмикається окремо */
#define pr_fmt(fmt) KBUILD_MODNAME ": " fmt

#include <linux/init.h>
#include <linux/module.h>
#include <linux/panic.h>	/* add_taint(), TAINT_*; у старих ядрах — linux/kernel.h */
#ifdef LAB_GPL_SYMBOL
#include <linux/rcupdate.h>	/* synchronize_rcu() експортовано лише для GPL */
#endif

static int step;
module_param(step, int, 0444);
MODULE_PARM_DESC(step, "2 — WARN_ON(), 3 — add_taint(TAINT_USER), 9 — відмовити в init");

static int __init taintlab_init(void)
{
	pr_info("завантажуюся, step=%d\n", step);

	if (step == 2)
		WARN_ON_ONCE(1);				/* біт W */
	if (step == 3)
		add_taint(TAINT_USER, LOCKDEP_STILL_OK);	/* біт U */
	if (step == 9)
		return -EINVAL;					/* init провалився */

#ifdef LAB_GPL_SYMBOL
	synchronize_rcu();
#endif
	return 0;
}

static void __exit taintlab_exit(void)
{
	pr_info("вивантажуюся\n");
}

module_init(taintlab_init);
module_exit(taintlab_exit);

#ifdef LAB_PROPRIETARY
MODULE_LICENSE("Proprietary");
#else
MODULE_LICENSE("GPL");
#endif
#ifdef LAB_TEST
MODULE_INFO(test, "Y");		/* біт N; працює на ядрах від 6.0 */
#endif
MODULE_DESCRIPTION("Піддослідний модуль для спостереження за плямами");
