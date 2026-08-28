/* kallsyms_probe_module.c — Завантажуваний модуль ядра Linux (C Kernel-Space) */
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/kprobes.h>
#include <linux/kallsyms.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Unix Observability Course");
MODULE_DESCRIPTION("Демонстраційний модуль kallsyms та розв'язання неекспортованих символів у ядрі 5.7+");

typedef unsigned long (*kallsyms_lookup_name_t)(const char *name);
static kallsyms_lookup_name_t my_kallsyms_lookup_name = NULL;

static struct kprobe kp = {
    .symbol_name = "kallsyms_lookup_name",
};

static int __init kallsyms_demo_init(void)
{
    int ret;
    pr_info("=== [kallsyms_demo] Завантаження модуля ===\n");

    /* Крок 1: Реєстрація kprobe для отримання адреси kallsyms_lookup_name у ядрах 5.7+ */
    ret = register_kprobe(&kp);
    if (ret < 0) {
        pr_err("[kallsyms_demo] Не вдалося зареєструвати kprobe, помилка: %d\n", ret);
        return ret;
    }

    my_kallsyms_lookup_name = (kallsyms_lookup_name_t)kp.addr;
    unregister_kprobe(&kp);

    if (!my_kallsyms_lookup_name) {
        pr_err("[kallsyms_demo] Вказівник на kallsyms_lookup_name дорівнює NULL!\n");
        return -EINVAL;
    }

    pr_info("[kallsyms_demo] kallsyms_lookup_name знайдено за адресою: %ps (0x%px)\n",
            my_kallsyms_lookup_name, my_kallsyms_lookup_name);

    /* Крок 2: Динамічний пошук неекспортованого символу sys_call_table */
    unsigned long sys_call_table_addr = my_kallsyms_lookup_name("sys_call_table");
    if (sys_call_table_addr) {
        pr_info("[kallsyms_demo] sys_call_table знайдено за адресою: %pS\n",
                (void *)sys_call_table_addr);
    } else {
        pr_warn("[kallsyms_demo] Символ sys_call_table не знайдено.\n");
    }

    /* Крок 3: Демонстрація різних специфікаторів форматування %pS у printk */
    void *current_func_addr = (void *)kallsyms_demo_init;
    pr_info("[kallsyms_demo] %pS  : %pS\n", current_func_addr, current_func_addr);
    pr_info("[kallsyms_demo] %ps  : %ps\n", current_func_addr, current_func_addr);
    pr_info("[kallsyms_demo] %pB  : %pB\n", current_func_addr, current_func_addr);

    return 0;
}

static void __exit kallsyms_demo_exit(void)
{
    pr_info("=== [kallsyms_demo] Вивантаження модуля ===\n");
}

module_init(kallsyms_demo_init);
module_exit(kallsyms_demo_exit);
