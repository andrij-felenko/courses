#include <linux/init.h>
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/sysctl.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("sysctl demo");
MODULE_DESCRIPTION("Приклад реєстрації параметрів sysctl");

static int custom_debug_level = 0;
static int min_debug = 0;
static int max_debug = 5;

static char custom_node_name[64] = "linux-node-01";

static struct ctl_table custom_sysctl_table[] = {
    {
        .procname     = "debug_level",
        .data         = &custom_debug_level,
        .maxlen       = sizeof(int),
        .mode         = 0644,
        .proc_handler = proc_dointvec_minmax,
        .extra1       = &min_debug,
        .extra2       = &max_debug,
    },
    {
        .procname     = "node_name",
        .data         = custom_node_name,
        .maxlen       = sizeof(custom_node_name),
        .mode         = 0644,
        .proc_handler = proc_dostring,
    },
};

static struct ctl_table_header *custom_header;

static int __init custom_sysctl_init(void)
{
    /* Реєструємо параметри за шляхом /proc/sys/kernel/custom_tuning */
    custom_header = register_sysctl("kernel/custom_tuning", custom_sysctl_table);
    if (!custom_header) {
        pr_err("sysctl_demo: не вдалося зареєструвати таблицю sysctl\n");
        return -ENOMEM;
    }
    pr_info("sysctl_demo: параметри у /proc/sys/kernel/custom_tuning успішно створено\n");
    return 0;
}

static void __exit custom_sysctl_exit(void)
{
    if (custom_header) {
        unregister_sysctl_table(custom_header);
        pr_info("sysctl_demo: таблицю sysctl видалено\n");
    }
}

module_init(custom_sysctl_init);
module_exit(custom_sysctl_exit);
