#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/debugfs.h>
#include <linux/seq_file.h>
#include <linux/mutex.h>
#include <linux/uaccess.h>
#include <linux/atomic.h>
#include <linux/ktime.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Kernel Developer");
MODULE_DESCRIPTION("Demo Kernel Module with Custom debugfs Interface");
MODULE_VERSION("1.0");

#define LOG_MAX_ENTRIES 10
#define LOG_ENTRY_LEN 128

struct log_entry {
    u64 timestamp_ns;
    char message[LOG_ENTRY_LEN];
};

static struct dentry *demo_dir;
static atomic_t event_count = ATOMIC_INIT(0);
static bool logging_enabled = true;

static struct log_entry ring_buffer[LOG_MAX_ENTRIES];
static size_t ring_head = 0;
static size_t ring_count = 0;
static DEFINE_MUTEX(ring_lock);

/* Додавання нового запису до кільцевого буфера ядра */
static void add_event_log(const char *msg)
{
    if (!logging_enabled)
        return;

    mutex_lock(&ring_lock);
    
    ring_buffer[ring_head].timestamp_ns = ktime_get_real_ns();
    snprintf(ring_buffer[ring_head].message, LOG_ENTRY_LEN, "%s", msg);
    
    ring_head = (ring_head + 1) % LOG_MAX_ENTRIES;
    if (ring_count < LOG_MAX_ENTRIES)
        ring_count++;

    mutex_unlock(&ring_lock);
    atomic_inc(&event_count);
}

/* === Послідовний вивід seq_file для events_log === */
static int events_seq_show(struct seq_file *s, void *v)
{
    size_t i, idx;
    u64 sec, nsec;

    mutex_lock(&ring_lock);
    seq_printf(s, "=== INSPECTOR DEMO LOG (Total Events: %d) ===\n", atomic_read(&event_count));
    seq_printf(s, "%-20s | %s\n", "Timestamp (s.ns)", "Event Message");
    seq_printf(s, "-----------------------------------------------------\n");

    for (i = 0; i < ring_count; i++) {
        /* Обчислюємо індекс для зчитування від найстарішого запису до найновішого */
        if (ring_count < LOG_MAX_ENTRIES) {
            idx = i;
        } else {
            idx = (ring_head + i) % LOG_MAX_ENTRIES;
        }

        sec = ring_buffer[idx].timestamp_ns / 1000000000ULL;
        nsec = ring_buffer[idx].timestamp_ns % 1000000000ULL;

        seq_printf(s, "%llu.%09llu | %s\n", sec, nsec, ring_buffer[idx].message);
    }

    mutex_unlock(&ring_lock);
    return 0;
}

static int events_seq_open(struct inode *inode, struct file *file)
{
    return single_open(file, events_seq_show, NULL);
}

static const struct file_operations events_fops = {
    .owner   = THIS_MODULE,
    .open    = events_seq_open,
    .read    = seq_read,
    .llseek  = seq_lseek,
    .release = single_release,
};

/* === Обробник читання та запису для control === */
static ssize_t control_write(struct file *file, const char __user *user_buf,
                             size_t count, loff_t *ppos)
{
    char buf[16];
    size_t buf_size = min(count, sizeof(buf) - 1);

    if (copy_from_user(buf, user_buf, buf_size))
        return -EFAULT;

    buf[buf_size] = '\0';

    if (buf[0] == '1') {
        logging_enabled = true;
        add_event_log("Logging manually ENABLED via control file");
    } else if (buf[0] == '0') {
        add_event_log("Logging manually DISABLED via control file");
        logging_enabled = false;
    }

    return count;
}

static ssize_t control_read(struct file *file, char __user *user_buf,
                            size_t count, loff_t *ppos)
{
    char status_str[32];
    int len = snprintf(status_str, sizeof(status_str), "Enabled: %d\n", logging_enabled);
    return simple_read_from_buffer(user_buf, count, ppos, status_str, len);
}

static const struct file_operations control_fops = {
    .owner = THIS_MODULE,
    .read  = control_read,
    .write = control_write,
};

/* === Ініціалізація та вивантаження модуля === */
static int __init inspector_init(void)
{
    demo_dir = debugfs_create_dir("inspector_demo", NULL);
    if (IS_ERR(demo_dir)) {
        pr_err("kdebug_inspector: Failed to create debugfs directory\n");
        return PTR_ERR(demo_dir);
    }

    /* 1. Створюємо атомарний файл лічильника */
    debugfs_create_atomic_t("event_count", 0644, demo_dir, &event_count);

    /* 2. Створюємо файл керування */
    debugfs_create_file("control", 0644, demo_dir, NULL, &control_fops);

    /* 3. Створюємо seq_file журнал подій */
    debugfs_create_file("events_log", 0444, demo_dir, NULL, &events_fops);

    add_event_log("Module loaded successfully");
    pr_info("kdebug_inspector: Module initialized at /sys/kernel/debug/inspector_demo\n");
    return 0;
}

static void __exit inspector_exit(void)
{
    /* Рекурсивно вилучаємо каталог і всі вкладені файли */
    debugfs_remove_recursive(demo_dir);
    pr_info("kdebug_inspector: Module unloaded\n");
}

module_init(inspector_init);
module_exit(inspector_exit);
