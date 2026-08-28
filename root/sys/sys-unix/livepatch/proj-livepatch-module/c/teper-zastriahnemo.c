// SPDX-License-Identifier: GPL-2.0
#include <linux/module.h>
#include <linux/kthread.h>
#include <linux/sched.h>

static struct task_struct *victim_thread;

void victim_loop(void);

/* noinline і не static — щоб функція лишилася окремим символом.
 * Уся робота потоку відбувається ВСЕРЕДИНІ неї, тож її кадр лежить
 * на стеку потоку від першої до останньої миті.
 */
noinline void victim_loop(void)
{
        while (!kthread_should_stop())
                schedule_timeout_interruptible(HZ);
}

static int victim_fn(void *unused)
{
        victim_loop();
        return 0;
}

static int __init victim_init(void)
{
        victim_thread = kthread_run(victim_fn, NULL, "klp_victim");
        return PTR_ERR_OR_ZERO(victim_thread);
}

static void __exit victim_exit(void)
{
        kthread_stop(victim_thread);
}

module_init(victim_init);
module_exit(victim_exit);
MODULE_LICENSE("GPL");
