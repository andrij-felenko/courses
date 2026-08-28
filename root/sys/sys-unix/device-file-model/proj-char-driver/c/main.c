// SPDX-License-Identifier: GPL-2.0
#include <linux/cdev.h>
#include <linux/device.h>
#include <linux/err.h>
#include <linux/fs.h>
#include <linux/module.h>
#include <linux/mutex.h>
#include <linux/uaccess.h>

#define DEV_NAME  "lichylnyk"
#define BODY_MAX  64

static dev_t         lich_dev;      /* старший:молодший, видані ядром */
static struct cdev   lich_cdev;
static struct class *lich_class;

static DEFINE_MUTEX(lich_lock);
static unsigned long lich_opens;    /* тільки під lich_lock */

/* Увесь «вміст» файлу малює одна функція. Розміру наперед немає —
   отже, де кінець файлу, вирішує сам драйвер у lich_read().        */
static int lich_render(char *body, size_t cap)
{
	unsigned long n;

	mutex_lock(&lich_lock);
	n = lich_opens;
	mutex_unlock(&lich_lock);

	return scnprintf(body, cap, "відкриттів: %lu\n", n);
}

static int lich_open(struct inode *inode, struct file *filp)
{
	unsigned long n;

	mutex_lock(&lich_lock);
	n = ++lich_opens;
	mutex_unlock(&lich_lock);

	pr_info("lich: open, молодший %u, усього %lu\n", iminor(inode), n);
	return 0;
}

static int lich_release(struct inode *inode, struct file *filp)
{
	pr_info("lich: release\n");
	return 0;
}

static ssize_t lich_read(struct file *filp, char __user *buf,
			 size_t count, loff_t *ppos)
{
	char body[BODY_MAX];
	int  len = lich_render(body, sizeof body);

	/* Кінець файлу — наш обов'язок. Не повернемо нуля — cat не спиниться. */
	if (*ppos >= len)
		return 0;
	if (count > (size_t)(len - *ppos))
		count = len - *ppos;

	/* Повертає число НЕ скопійованих байтів; нуль означає успіх. */
	if (copy_to_user(buf, body + *ppos, count))
		return -EFAULT;

	*ppos += count;
	return count;
}

static ssize_t lich_write(struct file *filp, const char __user *buf,
			  size_t count, loff_t *ppos)
{
	char   kbuf[BODY_MAX];
	size_t n = min(count, sizeof(kbuf) - 1);

	if (copy_from_user(kbuf, buf, n))
		return -EFAULT;
	kbuf[n] = '\0';
	if (n && kbuf[n - 1] == '\n')
		kbuf[n - 1] = '\0';

	mutex_lock(&lich_lock);
	lich_opens = 0;
	mutex_unlock(&lich_lock);

	pr_info("lich: скинуто, прийшло %zu байтів: «%s»\n", count, kbuf);
	return count;   /* кажемо, що з'їли все: інакше запис повторять */
}

static const struct file_operations lich_fops = {
	.owner   = THIS_MODULE,   /* саме це тримає модуль, поки файл відкрито */
	.open    = lich_open,
	.release = lich_release,
	.read    = lich_read,
	.write   = lich_write,
};

static int __init lich_init(void)
{
	struct device *dev;
	int ret;

	ret = alloc_chrdev_region(&lich_dev, 0, 1, DEV_NAME);
	if (ret)
		return ret;

	/* Після cdev_add() пристрій живий: open може прийти наступної миті
	   й на іншому ядрі процесора. Усе, чого торкаються lich_*, має бути
	   готове ДО цього рядка.                                          */
	cdev_init(&lich_cdev, &lich_fops);
	lich_cdev.owner = THIS_MODULE;
	ret = cdev_add(&lich_cdev, lich_dev, 1);
	if (ret)
		goto err_region;

	lich_class = class_create("lich");   /* із ядра 6.4 — один аргумент */
	if (IS_ERR(lich_class)) {
		ret = PTR_ERR(lich_class);
		goto err_cdev;
	}

	dev = device_create(lich_class, NULL, lich_dev, NULL, DEV_NAME);
	if (IS_ERR(dev)) {
		ret = PTR_ERR(dev);
		goto err_class;
	}

	pr_info("lich: готово, номери %d:%d\n",
		MAJOR(lich_dev), MINOR(lich_dev));
	return 0;

err_class:
	class_destroy(lich_class);
err_cdev:
	cdev_del(&lich_cdev);
err_region:
	unregister_chrdev_region(lich_dev, 1);
	return ret;
}

static void __exit lich_exit(void)
{
	device_destroy(lich_class, lich_dev);
	class_destroy(lich_class);
	cdev_del(&lich_cdev);
	unregister_chrdev_region(lich_dev, 1);
	pr_info("lich: пішли\n");
}

module_init(lich_init);
module_exit(lich_exit);

MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("Символьний пристрій-лічильник відкриттів");
