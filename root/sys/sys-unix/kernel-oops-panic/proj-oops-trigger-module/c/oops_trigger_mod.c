/* oops_trigger_mod.c — Симулятор аварійних ситуацій ядра Linux */
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/proc_fs.h>
#include <linux/uaccess.h>
#include <linux/timer.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Kernel Observability Guide");
MODULE_DESCRIPTION("Module for triggering Oops and Panic for testing Kdump");

static struct proc_dir_entry *proc_entry;
static struct timer_list fault_timer;

/* Обробник таймера: виняток у контексті переривання (IRQ Context) */
static void irq_fault_timer_handler(struct timer_list *t)
{
    int *null_ptr = NULL;
    pr_emerg("oops_trigger: Triggering NULL dereference in IRQ handler!\n");
    /* Збій у контексті переривання неминуче трансформується у Kernel Panic */
    *null_ptr = 0xDEADBEEF;
}

static ssize_t oops_proc_write(struct file *file, const char __user *buffer,
                               size_t count, loff_t *pos)
{
    char kbuf[32];
    if (count >= sizeof(kbuf))
        return -EINVAL;

    if (copy_from_user(kbuf, buffer, count))
        return -EFAULT;

    kbuf[count] = '\0';
    if (count > 0 && kbuf[count - 1] == '\n')
        kbuf[count - 1] = '\0';

    if (strcmp(kbuf, "null") == 0) {
        int *ptr = NULL;
        pr_emerg("oops_trigger: Executing NULL pointer dereference in process context...\n");
        *ptr = 42; /* Простий Oops (за замовчуванням вбиває лише поточний процес) */
    } else if (strcmp(kbuf, "panic") == 0) {
        pr_emerg("oops_trigger: Calling panic() directly!\n");
        panic("oops_trigger: Manual execution of panic()");
    } else if (strcmp(kbuf, "irq_null") == 0) {
        pr_emerg("oops_trigger: Scheduling timer for IRQ fault in 100ms...\n");
        timer_setup(&fault_timer, irq_fault_timer_handler, 0);
        mod_timer(&fault_timer, jiffies + msecs_to_jiffies(100));
    } else if (strcmp(kbuf, "ro_write") == 0) {
        char *ro_text = (char *)oops_proc_write;
        pr_emerg("oops_trigger: Attempting to write to read-only kernel text segment...\n");
        *ro_text = 0x90; /* Порушення прав доступу до сторінки тексту ядра */
    } else {
        pr_info("oops_trigger: Unknown command '%s'. Supported: null, panic, irq_null, ro_write\n", kbuf);
    }

    return count;
}

static const struct proc_ops oops_proc_ops = {
    .proc_write = oops_proc_write,
};

static int __init oops_trigger_init(void)
{
    proc_entry = proc_create("oops_trigger", 0200, NULL, &oops_proc_ops);
    if (!proc_entry)
        return -ENOMEM;

    pr_info("oops_trigger: Loaded. Write to /proc/oops_trigger to test faults.\n");
    return 0;
}

static void __exit oops_trigger_exit(void)
{
    del_timer_sync(&fault_timer);
    if (proc_entry)
        proc_remove(proc_entry);
    pr_info("oops_trigger: Unloaded.\n");
}

module_init(oops_trigger_init);
module_exit(oops_trigger_exit);
