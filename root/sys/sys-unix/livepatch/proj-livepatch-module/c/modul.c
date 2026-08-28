// SPDX-License-Identifier: GPL-2.0
#define pr_fmt(fmt) KBUILD_MODNAME ": " fmt

#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/livepatch.h>
#include <linux/seq_file.h>
#include <linux/kthread.h>
#include <linux/sched.h>

/* Нове тіло cmdline_proc_show(). Підпис має збігатися ДО КРАПКИ:
 * компілятор його не звірить — .new_func оголошений як void *.
 */
static int livepatch_cmdline_proc_show(struct seq_file *m, void *v)
{
        seq_printf(m, "%s\n", "цю машину залатано наживо");
        return 0;
}

/* Нове тіло victim_loop() з модуля klp_victim (див. нижче). */
static void livepatch_victim_loop(void)
{
        pr_info("нова версія циклу\n");
        while (!kthread_should_stop())
                schedule_timeout_interruptible(HZ);
}

static struct klp_func vmlinux_funcs[] = {
        { .old_name = "cmdline_proc_show",
          .new_func = livepatch_cmdline_proc_show }, { }
};

static struct klp_func victim_funcs[] = {
        { .old_name = "victim_loop",
          .new_func = livepatch_victim_loop }, { }
};

static struct klp_object objs[] = {
        { /* .name = NULL — саме ядро */
          .funcs = vmlinux_funcs },
        { .name  = "klp_victim",       /* ім'я модуля, як у /proc/modules */
          .funcs = victim_funcs },
        { }
};

static struct klp_patch patch = {
        .mod  = THIS_MODULE,
        .objs = objs,
};

static int livepatch_demo_init(void)
{
        return klp_enable_patch(&patch);
}

static void livepatch_demo_exit(void) { }

module_init(livepatch_demo_init);
module_exit(livepatch_demo_exit);
MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("Латка навчальна");
MODULE_INFO(livepatch, "Y");
