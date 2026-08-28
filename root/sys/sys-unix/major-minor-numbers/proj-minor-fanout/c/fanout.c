/* fanout.c — один драйвер, чотири незалежні примірники */
#include <linux/cdev.h>
#include <linux/device.h>
#include <linux/fs.h>
#include <linux/init.h>
#include <linux/module.h>
#include <linux/mutex.h>
#include <linux/uaccess.h>

#define FANOUT_COUNT 4
#define FANOUT_SIZE  512

struct fanout_slot {
    struct mutex lock;
    char   buf[FANOUT_SIZE];
    size_t len;
};

static struct fanout_slot slots[FANOUT_COUNT];
static dev_t          first;          /* пара «виданий старший, молодший 0» */
static struct cdev    fanout_cdev;
static struct class  *fanout_class;

static int fanout_open(struct inode *inode, struct file *file)
{
    unsigned int idx = MINOR(inode->i_rdev);   /* те саме, що iminor(inode) */

    if (idx >= FANOUT_COUNT)
        return -ENXIO;
    file->private_data = &slots[idx];          /* далі номер не потрібен */
    return 0;
}

static ssize_t fanout_read(struct file *file, char __user *ubuf,
                           size_t count, loff_t *ppos)
{
    struct fanout_slot *s = file->private_data;
    ssize_t n;

    if (mutex_lock_interruptible(&s->lock))
        return -ERESTARTSYS;
    n = simple_read_from_buffer(ubuf, count, ppos, s->buf, s->len);
    mutex_unlock(&s->lock);
    return n;
}

static ssize_t fanout_write(struct file *file, const char __user *ubuf,
                            size_t count, loff_t *ppos)
{
    struct fanout_slot *s = file->private_data;
    ssize_t n;

    if (mutex_lock_interruptible(&s->lock))
        return -ERESTARTSYS;
    n = simple_write_to_buffer(s->buf, FANOUT_SIZE, ppos, ubuf, count);
    if (n > 0)
        s->len = *ppos;      /* довжина = де скінчився останній запис */
    mutex_unlock(&s->lock);
    return n;
}

static const struct file_operations fanout_fops = {
    .owner  = THIS_MODULE,
    .open   = fanout_open,
    .read   = fanout_read,
    .write  = fanout_write,
    .llseek = default_llseek,
};

static int __init fanout_init(void)
{
    int i, err;

    err = alloc_chrdev_region(&first, 0, FANOUT_COUNT, "fanout");
    if (err)
        return err;

    for (i = 0; i < FANOUT_COUNT; i++)
        mutex_init(&slots[i].lock);

    cdev_init(&fanout_cdev, &fanout_fops);
    fanout_cdev.owner = THIS_MODULE;
    err = cdev_add(&fanout_cdev, first, FANOUT_COUNT);   /* ВЕСЬ відтинок */
    if (err)
        goto err_region;

    fanout_class = class_create("fanout");               /* ядро 6.4 і новіші */
    if (IS_ERR(fanout_class)) {
        err = PTR_ERR(fanout_class);
        goto err_cdev;
    }

    for (i = 0; i < FANOUT_COUNT; i++) {
        struct device *d = device_create(fanout_class, NULL,
                                         MKDEV(MAJOR(first), i), NULL,
                                         "fanout%d", i);
        if (IS_ERR(d)) {
            err = PTR_ERR(d);
            goto err_devices;
        }
    }

    pr_info("fanout: старший %d, молодші %d…%d\n", MAJOR(first),
            MINOR(first), MINOR(first) + FANOUT_COUNT - 1);
    return 0;

err_devices:
    while (--i >= 0)
        device_destroy(fanout_class, MKDEV(MAJOR(first), i));
    class_destroy(fanout_class);
err_cdev:
    cdev_del(&fanout_cdev);
err_region:
    unregister_chrdev_region(first, FANOUT_COUNT);
    return err;
}

static void __exit fanout_exit(void)
{
    int i;

    for (i = 0; i < FANOUT_COUNT; i++)
        device_destroy(fanout_class, MKDEV(MAJOR(first), i));
    class_destroy(fanout_class);
    cdev_del(&fanout_cdev);
    unregister_chrdev_region(first, FANOUT_COUNT);
}

module_init(fanout_init);
module_exit(fanout_exit);
MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("Один драйвер на чотири примірники, розведені молодшим номером");
