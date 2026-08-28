#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/debugfs.h>
#include <linux/seq_file.h>
#include <linux/mutex.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Courses reference example");
MODULE_DESCRIPTION("Приклад інтеграції debugfs та seq_file");

/* Структури даних ядра для керування вузлами debugfs */
static struct dentry *demo_dir;
static u32 packet_count = 0;
static bool debug_mode_enabled = false;

/* М'ютекс для захисту змінних стану від паралельного читання/запису */
static DEFINE_MUTEX(state_lock);

/*
 * Обробник виводу даних через seq_file.
 * Функція викликається ядром для форматування текстового виводу.
 * seq_printf гарантує безпечне виділення пам'яті та усуває ризик
 * переповнення буфера при формуванні великих звітів.
 */
static int demo_seq_show(struct seq_file *m, void *v)
{
    mutex_lock(&state_lock);
    seq_printf(m, "===================================\n");
    seq_printf(m, " СТАТУС ДРАЙВЕРА DEMO_DRIVER       \n");
    seq_printf(m, "===================================\n");
    seq_printf(m, "Опрацьовані пакети : %u\n", packet_count);
    seq_printf(m, "Режим налагодження : %s\n", debug_mode_enabled ? "УВІМКНЕНО" : "ВИМКНЕНО");
    seq_printf(m, "Адреса лічильника  : %px\n", m->private);
    seq_printf(m, "===================================\n");
    mutex_unlock(&state_lock);
    return 0;
}

/* Обробник відкриття файлу через single_open */
static int demo_seq_open(struct inode *inode, struct file *file)
{
    return single_open(file, demo_seq_show, inode->i_private);
}

/*
 * Таблиця операцій над файлом debugfs.
 * Використовуються стандартні макроси seq_read, seq_lseek та single_release,
 * що мінімізує кількість написаного коду.
 */
static const struct file_operations demo_fops = {
    .owner   = THIS_MODULE,
    .open    = demo_seq_open,
    .read    = seq_read,
    .llseek  = seq_lseek,
    .release = single_release,
};

static int __init demo_debugfs_init(void)
{
    pr_info("demo_driver: Ініціалізація вузлів у debugfs...\n");

    /* Створення каталогу /sys/kernel/debug/demo_driver */
    demo_dir = debugfs_create_dir("demo_driver", NULL);
    if (IS_ERR(demo_dir)) {
        pr_err("demo_driver: Помилка створення каталогу в debugfs (%ld)\n", PTR_ERR(demo_dir));
        return PTR_ERR(demo_dir);
    }

    /* Експорт 32-бітного беззнакового цілого числа (права 0644 — читання/запис) */
    debugfs_create_u32("packet_count", 0644, demo_dir, &packet_count);

    /* Експорт булевого прапорця (права 0644) */
    debugfs_create_bool("debug_enabled", 0644, demo_dir, &debug_mode_enabled);

    /*
     * Експорт користувацького вузла seq_file (права 0444 — лише читання).
     * Четвертий аргумент — приватні дані вузла: ядро кладе його в
     * inode->i_private, звідки demo_seq_open передає далі в m->private.
     */
    debugfs_create_file("status_report", 0444, demo_dir, &packet_count, &demo_fops);

    pr_info("demo_driver: Успішно зареєстровано вузли у /sys/kernel/debug/demo_driver\n");
    return 0;
}

static void __exit demo_debugfs_exit(void)
{
    pr_info("demo_driver: Вилучення вузлів із debugfs...\n");

    /*
     * Рекурсивне видалення каталогу та всіх його елементів.
     * Запобігає витоку пам'яті та залишенню «сирітських» dentry в ядрі.
     */
    debugfs_remove_recursive(demo_dir);
    pr_info("demo_driver: Модуль вивантажено.\n");
}

module_init(demo_debugfs_init);
module_exit(demo_debugfs_exit);
