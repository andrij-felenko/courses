#include <linux/module.h>
#include <linux/fs.h>
#include <linux/uaccess.h>
#include <linux/cdev.h>
#include <linux/slab.h>
#include <linux/poll.h>

#define DEVICE_NAME "mychardev"
#define BUFFER_SIZE 1024

static dev_t dev_num;
static struct cdev my_cdev;
static char device_buffer[BUFFER_SIZE];
static size_t data_size = 0;
static DEFINE_MUTEX(dev_mutex);
static DECLARE_WAIT_QUEUE_HEAD(read_queue);

static int dev_open(struct inode *inodep, struct file *filep)
{
    pr_info("mychardev: пристрій відкрито pid=%d\n", current->pid);
    return 0;
}

static int dev_release(struct inode *inodep, struct file *filep)
{
    pr_info("mychardev: пристрій закрито\n");
    return 0;
}

static ssize_t dev_read(struct file *filep, char __user *buffer, size_t len, loff_t *offset)
{
    ssize_t bytes_to_read;

    if (mutex_lock_interruptible(&dev_mutex))
        return -ERESTARTSYS;

    while (data_size == 0) {
        mutex_unlock(&dev_mutex);
        if (filep->f_flags & O_NONBLOCK)
            return -EAGAIN;
        if (wait_event_interruptible(read_queue, data_size > 0))
            return -ERESTARTSYS;
        if (mutex_lock_interruptible(&dev_mutex))
            return -ERESTARTSYS;
    }

    if (*offset >= data_size) {
        mutex_unlock(&dev_mutex);
        return 0; /* EOF */
    }

    bytes_to_read = min(len, (size_t)(data_size - *offset));

    if (copy_to_user(buffer, device_buffer + *offset, bytes_to_read) != 0) {
        mutex_unlock(&dev_mutex);
        return -EFAULT;
    }

    *offset += bytes_to_read;
    mutex_unlock(&dev_mutex);

    return bytes_to_read;
}

static ssize_t dev_write(struct file *filep, const char __user *buffer, size_t len, loff_t *offset)
{
    ssize_t bytes_to_write;

    if (mutex_lock_interruptible(&dev_mutex))
        return -ERESTARTSYS;

    bytes_to_write = min(len, (size_t)(BUFFER_SIZE - *offset));
    if (bytes_to_write <= 0) {
        mutex_unlock(&dev_mutex);
        return -ENOSPC;
    }

    if (copy_from_user(device_buffer + *offset, buffer, bytes_to_write) != 0) {
        mutex_unlock(&dev_mutex);
        return -EFAULT;
    }

    *offset += bytes_to_write;
    if (*offset > data_size)
        data_size = *offset;

    wake_up_interruptible(&read_queue);
    mutex_unlock(&dev_mutex);
    return bytes_to_write;
}

static __poll_t dev_poll(struct file *filep, struct poll_table_struct *wait)
{
    __poll_t mask = 0;

    poll_wait(filep, &read_queue, wait);

    mutex_lock(&dev_mutex);
    if (data_size > 0)
        mask |= EPOLLIN | EPOLLRDNORM;
    if (data_size < BUFFER_SIZE)
        mask |= EPOLLOUT | EPOLLWRNORM;
    mutex_unlock(&dev_mutex);

    return mask;
}

static loff_t dev_llseek(struct file *filep, loff_t offset, int whence)
{
    loff_t new_pos;

    if (mutex_lock_interruptible(&dev_mutex))
        return -ERESTARTSYS;

    switch (whence) {
    case SEEK_SET:
        new_pos = offset;
        break;
    case SEEK_CUR:
        new_pos = filep->f_pos + offset;
        break;
    case SEEK_END:
        new_pos = data_size + offset;
        break;
    default:
        mutex_unlock(&dev_mutex);
        return -EINVAL;
    }

    if (new_pos < 0 || new_pos > BUFFER_SIZE) {
        mutex_unlock(&dev_mutex);
        return -EINVAL;
    }

    filep->f_pos = new_pos;
    mutex_unlock(&dev_mutex);
    return new_pos;
}

static const struct file_operations fops = {
    .owner          = THIS_MODULE,
    .open           = dev_open,
    .release        = dev_release,
    .read           = dev_read,
    .write          = dev_write,
    .poll           = dev_poll,
    .llseek         = dev_llseek,
};

static int __init mychardev_init(void)
{
    int ret;

    ret = alloc_chrdev_region(&dev_num, 0, 1, DEVICE_NAME);
    if (ret < 0)
        return ret;

    cdev_init(&my_cdev, &fops);
    my_cdev.owner = THIS_MODULE;

    ret = cdev_add(&my_cdev, dev_num, 1);
    if (ret < 0) {
        unregister_chrdev_region(dev_num, 1);
        return ret;
    }

    pr_info("mychardev: зареєстровано з major = %d, minor = %d\n",
            MAJOR(dev_num), MINOR(dev_num));
    return 0;
}

static void __exit mychardev_exit(void)
{
    cdev_del(&my_cdev);
    unregister_chrdev_region(dev_num, 1);
    pr_info("mychardev: модуль вивантажено\n");
}

module_init(mychardev_init);
module_exit(mychardev_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Unix Architecture Guide");
MODULE_DESCRIPTION("Приклад реалізації struct file_operations для символьного драйвера");
