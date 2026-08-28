// SPDX-License-Identifier: GPL-2.0
#define pr_fmt(fmt) KBUILD_MODNAME ": " fmt

#include <linux/module.h>
#include <linux/jump_label.h>
#include <linux/moduleparam.h>

#ifndef CONFIG_JUMP_LABEL
#error "Треба ядро з CONFIG_JUMP_LABEL=y, інакше це буде звичайний if"
#endif

static DEFINE_STATIC_KEY_FALSE(demo_key);

unsigned long demo_arg = 7;
unsigned long demo_hot(unsigned long x);

/* Гаряча функція. noinline і не static — щоб лишилася окремим
 * символом і потрапила в /proc/kallsyms під власним іменем.
 */
noinline unsigned long demo_hot(unsigned long x)
{
        if (static_branch_unlikely(&demo_key))
                return x * 3 + 1;
        return x + 1;
}

/* Показати байти в кожному місці, яке цей модуль патчить. */
static void demo_dump(const char *when)
{
        struct jump_entry *e = THIS_MODULE->jump_entries;
        unsigned int i, n = THIS_MODULE->num_jump_entries;

        for (i = 0; i < n; i++) {
                const u8 *code = (const u8 *)jump_entry_code(&e[i]);

                pr_info("%s: %pS @ %px -> %5ph\n", when, code, code, code);
        }
        pr_info("%s: demo_hot(%lu) = %lu\n", when, demo_arg, demo_hot(demo_arg));
}

static bool enabled;

static int demo_set(const char *val, const struct kernel_param *kp)
{
        bool was = enabled;
        int ret = param_set_bool(val, kp);   /* пише в &enabled */

        if (ret)
                return ret;
        if (enabled == was)
                return 0;

        /* Обидві беруть м'ютекс і cpus_read_lock() — тобто можуть заснути.
         * Тут це безпечно: запис у /sys приходить у контексті процесу.
         */
        if (enabled)
                static_branch_enable(&demo_key);
        else
                static_branch_disable(&demo_key);

        demo_dump(enabled ? "після enable" : "після disable");
        return 0;
}

static const struct kernel_param_ops demo_ops = {
        .set = demo_set,
        .get = param_get_bool,
};
module_param_cb(enabled, &demo_ops, &enabled, 0644);
MODULE_PARM_DESC(enabled, "0/1 — перемкнути статичний ключ");

static int __init demo_init(void)
{
        demo_dump("на старті");
        return 0;
}

static void __exit demo_exit(void) { }

module_init(demo_init);
module_exit(demo_exit);
MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("Статичний ключ під мікроскопом");
