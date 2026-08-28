#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/fs.h>
#include <linux/kernfs.h>
#include <linux/seq_file.h>
#include <linux/slab.h>
#include <linux/uaccess.h>
#include <linux/utsname.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Kernel Architecture Course");
MODULE_DESCRIPTION("Autonomous kernfs-based pseudo filesystem demo");
MODULE_VERSION("1.0");

#define DEMO_FS_MAGIC 0x5053464B /* байти "KFSP" у порядку little-endian */

static struct kernfs_root *demo_root;
static struct kernfs_node *control_dir;
static struct kernfs_node *info_node;
static struct kernfs_node *status_node;

/* Атомарний лічильник для демонстрації безпечної роботи з даними */
static atomic_t global_counter = ATOMIC_INIT(100);

/* --- Метод 1: seq_show для файла /info --- */
static int demo_info_show(struct seq_file *sf, void *v)
{
    seq_printf(sf, "=== Demo Kernfs Subsystem ===\n");
    seq_printf(sf, "Status: ACTIVE\n");
    seq_printf(sf, "Global Counter Value: %d\n", atomic_read(&global_counter));
    seq_printf(sf, "Kernel Release: %s\n", init_utsname()->release);
    seq_printf(sf, "Architecture Footprint: kernfs_node size = %zu B\n",
               sizeof(struct kernfs_node));
    return 0;
}

static struct kernfs_ops info_ops = {
    .seq_show = demo_info_show,
};

/* --- Метод 2: read/write для файла /control/status --- */
static int demo_status_show(struct seq_file *sf, void *v)
{
    seq_printf(sf, "%d\n", atomic_read(&global_counter));
    return 0;
}

static ssize_t demo_status_write(struct kernfs_open_file *of,
                                 char *buf, size_t count, loff_t off)
{
    int val, err;

    /* Шар kernfs гарантує, що buf завершується нуль-термінатором '\0' */
    err = kstrtoint(strstrip(buf), 10, &val);
    if (err) {
        pr_warn("demo_kernfs: Invalid integer format: %s\n", buf);
        return err;
    }

    if (val < 0 || val > 1000000) {
        pr_warn("demo_kernfs: Counter value out of range (0..1000000): %d\n", val);
        return -EINVAL;
    }

    atomic_set(&global_counter, val);
    pr_info("demo_kernfs: global_counter successfully updated to %d\n", val);

    return count;
}

static struct kernfs_ops status_ops = {
    .seq_show = demo_status_show,
    .write    = demo_status_write,
};

/* --- Монтування та ініціалізація суперблоку VFS --- */
static struct dentry *demo_mount(struct file_system_type *fs_type,
                                 int flags, const char *dev_name, void *data)
{
    /* kernfs_mount автоматично зв'язує VFS superblock із нашим kernfs_root */
    return kernfs_mount(fs_type, flags, demo_root, DEMO_FS_MAGIC, NULL);
}

static void demo_kill_sb(struct super_block *sb)
{
    /* Автоматична деінсталяція VFS dentry та inode при розмонтуванні */
    kernfs_kill_sb(sb);
}

static struct file_system_type demo_fs_type = {
    .name     = "demo_kernfs",
    .mount    = demo_mount,
    .kill_sb  = demo_kill_sb,
    .owner    = THIS_MODULE,
};

/* --- Ініціалізація модуля ядра --- */
static int __init demo_kernfs_init(void)
{
    int ret;

    pr_info("demo_kernfs: Initializing custom kernfs demonstration module...\n");

    /* 1. Створюємо корінь деревного графа kernfs */
    demo_root = kernfs_create_root(NULL, 0, NULL);
    if (IS_ERR(demo_root)) {
        pr_err("demo_kernfs: Failed to create kernfs root structure\n");
        return PTR_ERR(demo_root);
    }

    /* 2. Створюємо файл /info у корені з правами читання 0444 */
    info_node = kernfs_create_file(demo_root->kn, "info", 0444, 0,
                                   &info_ops, NULL);
    if (IS_ERR(info_node)) {
        ret = PTR_ERR(info_node);
        pr_err("demo_kernfs: Failed to create /info node (err=%d)\n", ret);
        goto err_destroy_root;
    }

    /* 3. Створюємо каталог /control з правами 0755 */
    control_dir = kernfs_create_dir(demo_root->kn, "control", 0755, NULL);
    if (IS_ERR(control_dir)) {
        ret = PTR_ERR(control_dir);
        pr_err("demo_kernfs: Failed to create /control directory (err=%d)\n", ret);
        goto err_destroy_root;
    }

    /* 4. Створюємо файл /control/status з правами читання/запису 0644 */
    status_node = kernfs_create_file(control_dir, "status", 0644, 0,
                                     &status_ops, NULL);
    if (IS_ERR(status_node)) {
        ret = PTR_ERR(status_node);
        pr_err("demo_kernfs: Failed to create /control/status node (err=%d)\n", ret);
        goto err_destroy_root;
    }

    /* 5. Реєструємо тип ФС у глобальному реєстрі VFS */
    ret = register_filesystem(&demo_fs_type);
    if (ret) {
        pr_err("demo_kernfs: Failed to register demo_kernfs filesystem type\n");
        goto err_destroy_root;
    }

    pr_info("demo_kernfs: Subsystem initialized cleanly. Mount using: mount -t demo_kernfs none /mnt/demo_fs\n");
    return 0;

err_destroy_root:
    /* При виникненні помилок рекурсивно очищаємо виділені вузли */
    kernfs_destroy_root(demo_root);
    return ret;
}

/* --- Очищення ресурсів при розвантаженні модуля --- */
static void __exit demo_kernfs_exit(void)
{
    pr_info("demo_kernfs: Unregistering filesystem from VFS...\n");
    unregister_filesystem(&demo_fs_type);

    /*
     * kernfs_destroy_root рекурсивно проходить по всіх вузлах,
     * викликає kernfs_drain() для кожного з них, очікує завершення
     * активних файлових операцій read/write та звільняє пам'ять.
     */
    kernfs_destroy_root(demo_root);
    pr_info("demo_kernfs: Module unloaded with 100%% active reference drain safety.\n");
}

module_init(demo_kernfs_init);
module_exit(demo_kernfs_exit);
