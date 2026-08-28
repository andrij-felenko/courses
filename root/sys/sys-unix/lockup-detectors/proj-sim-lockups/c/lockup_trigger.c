/*
 * lockup_trigger.c — Модуль для контрольованої симуляції зависань ядра Linux.
 * Призначений виключно для налагодження та тестування в ізольованому середовищі.
 */
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/debugfs.h>
#include <linux/delay.h>
#include <linux/kthread.h>
#include <linux/sched.h>
#include <linux/spinlock.h>
#include <linux/interrupt.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Unix & Linux Observability Guide");
MODULE_DESCRIPTION("Synthetic Soft/Hard Lockup and Hung Task Generator");

static struct dentry *debugfs_dir;
static struct task_struct *hung_task_kthread;

/* Спінлок для симуляції довгого утримання в Soft Lockup */
static DEFINE_SPINLOCK(dummy_spinlock);

/*
 * 1. Генератор Soft Lockup:
 * Захоплює спінлок (що вимикає витіснення на цьому CPU) і крутиться у глухому циклі
 * протягом 25 секунд. Апаратні IRQ активні, проте планувальник не може перемкнути задачу.
 */
static ssize_t trigger_soft_lockup_write(struct file *file, const char __user *user_buf,
                                        size_t count, loff_t *ppos)
{
    pr_warn("lockup_trigger: [CPU#%d] Ініціалізація Soft Lockup на 25 секунд...\n",
            raw_smp_processor_id());

    /* Захоплюємо spinlock без вимикання IRQ — преемпція вимкнена, таймери цокають */
    spin_lock(&dummy_spinlock);
    
    /* Цикл активного очікування (25000 мс > 2 * watchdog_thresh = 20 с) */
    mdelay(25000);
    
    spin_unlock(&dummy_spinlock);

    pr_info("lockup_trigger: [CPU#%d] Soft Lockup завершено успішно\n",
            raw_smp_processor_id());
    return count;
}

/*
 * 2. Генератор Hard Lockup:
 * Вимикає апаратні переривання на поточному ядрі CPU через local_irq_disable()
 * і входить у безкінечний цикл. Звичайні таймери hrtimer паралізовані.
 * Виявити цей стан здатне лише немасковане переривання NMI.
 */
static ssize_t trigger_hard_lockup_write(struct file *file, const char __user *user_buf,
                                        size_t count, loff_t *ppos)
{
    pr_emerg("lockup_trigger: [CPU#%d] Ініціалізація Hard Lockup (local_irq_disable)...\n",
             raw_smp_processor_id());

    /* Вимикаємо локальні апаратні переривання процесора (скидаємо прапорець IF в EFLAGS) */
    local_irq_disable();

    /* Безкінечний мертвий цикл ядра */
    while (1) {
        cpu_relax();
    }

    /* Сюди ядро не дійде ніколи */
    return count;
}

/*
 * 3. Функція ядерного потоку для симуляції Hung Task (D-state)
 */
static int hung_task_worker(void *data)
{
    pr_warn("lockup_trigger: Потік hung_task_worker запущено (PID: %d), перехід у D-state на 150 с...\n",
            current->pid);

    /* Переводимо задачу в непереривний сон */
    set_current_state(TASK_UNINTERRUPTIBLE);

    /* Засинаємо на 150 секунд (більше за замовчуваний тайм-аут 120 с) */
    schedule_timeout(msecs_to_jiffies(150000));

    pr_info("lockup_trigger: Потік hung_task_worker прокинувся\n");
    return 0;
}

static ssize_t trigger_hung_task_write(struct file *file, const char __user *user_buf,
                                      size_t count, loff_t *ppos)
{
    hung_task_kthread = kthread_run(hung_task_worker, NULL, "kworker_hung_sim");
    if (IS_ERR(hung_task_kthread)) {
        pr_err("lockup_trigger: Не вдалося створити kthread\n");
        return PTR_ERR(hung_task_kthread);
    }
    return count;
}

static const struct file_operations soft_fops = {
    .owner = THIS_MODULE,
    .write = trigger_soft_lockup_write,
};

static const struct file_operations hard_fops = {
    .owner = THIS_MODULE,
    .write = trigger_hard_lockup_write,
};

static const struct file_operations hung_fops = {
    .owner = THIS_MODULE,
    .write = trigger_hung_task_write,
};

static int __init lockup_trigger_init(void)
{
    debugfs_dir = debugfs_create_dir("lockup_trigger", NULL);
    if (!debugfs_dir)
        return -ENOMEM;

    debugfs_create_file("trigger_soft_lockup", 0200, debugfs_dir, NULL, &soft_fops);
    debugfs_create_file("trigger_hard_lockup", 0200, debugfs_dir, NULL, &hard_fops);
    debugfs_create_file("trigger_hung_task",   0200, debugfs_dir, NULL, &hung_fops);

    pr_info("lockup_trigger: Модуль завантажено. Вузли debugfs створено.\n");
    return 0;
}

static void __exit lockup_trigger_exit(void)
{
    debugfs_remove_recursive(debugfs_dir);
    pr_info("lockup_trigger: Модуль вивантажено.\n");
}

module_init(lockup_trigger_init);
module_exit(lockup_trigger_exit);
