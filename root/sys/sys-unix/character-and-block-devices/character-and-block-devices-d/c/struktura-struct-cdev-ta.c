#include <linux/module.h>
#include <linux/fs.h>
#include <linux/cdev.h>
#include <linux/uaccess.h>

static dev_t dev_num;
static struct cdev my_cdev;

static ssize_t my_read(struct file *filp, char __user *buf, size_t count, loff_t *f_pos) {
    char data[] = "Hello from cdev!\n";
    size_t len = sizeof(data) - 1;
    
    if (*f_pos >= len) return 0; // EOF
    if (count > len - *f_pos) count = len - *f_pos;
    
    if (copy_to_user(buf, data + *f_pos, count))
        return -EFAULT;
        
    *f_pos += count;
    return count;
}

static const struct file_operations fops = {
    .owner = THIS_MODULE,
    .read = my_read,
};

static int __init my_driver_init(void) {
    alloc_chrdev_region(&dev_num, 0, 1, "my_cdev_device");
    cdev_init(&my_cdev, &fops);
    cdev_add(&my_cdev, dev_num, 1);
    return 0;
}
