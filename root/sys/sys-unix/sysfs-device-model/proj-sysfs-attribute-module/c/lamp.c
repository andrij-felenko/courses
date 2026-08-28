// lamp.c — пристрій з одним керованим значенням
#include <linux/module.h>
#include <linux/device.h>
#include <linux/err.h>
#include <linux/sysfs.h>
#include <linux/kstrtox.h>

#define LAMP_MAX 100

static unsigned int lamp_level = 50;        /* стан «заліза» */

/* читання: значення форматується просто в буфер, який дало ядро */
static ssize_t brightness_show(struct device *dev,
			       struct device_attribute *attr, char *buf)
{
	return sysfs_emit(buf, "%u\n", READ_ONCE(lamp_level));
}

/* запис: розібрати текст, перевірити межі, спожити весь буфер */
static ssize_t brightness_store(struct device *dev,
				struct device_attribute *attr,
				const char *buf, size_t count)
{
	unsigned int val;
	int err;

	err = kstrtouint(buf, 10, &val);    /* кінцевий '\n' від echo пробачається */
	if (err)
		return err;                 /* -EINVAL дійде до write() як errno */
	if (val > LAMP_MAX)
		return -ERANGE;

	WRITE_ONCE(lamp_level, val);
	dev_info(dev, "brightness set to %u\n", val);
	return count;                       /* спожито все */
}
static DEVICE_ATTR_RW(brightness);          /* → dev_attr_brightness, права 0644 */

static ssize_t max_brightness_show(struct device *dev,
				   struct device_attribute *attr, char *buf)
{
	return sysfs_emit(buf, "%u\n", LAMP_MAX);
}
static DEVICE_ATTR_RO(max_brightness);      /* → права 0444 */

static struct attribute *lamp_attrs[] = {
	&dev_attr_brightness.attr,
	&dev_attr_max_brightness.attr,
	NULL,
};
ATTRIBUTE_GROUPS(lamp);                     /* → lamp_group, lamp_groups */

static const struct class lamp_class = {
	.name = "lamp",
	.dev_groups = lamp_groups,          /* файли описані ДО реєстрації */
};

static struct device *lamp_dev;

static int __init lamp_init(void)
{
	int err;

	err = class_register(&lamp_class);
	if (err)
		return err;

	/* MKDEV(0,0) — пристрій без номерів, отже без файлу в /dev */
	lamp_dev = device_create(&lamp_class, NULL, MKDEV(0, 0), NULL, "lamp0");
	if (IS_ERR(lamp_dev)) {
		class_unregister(&lamp_class);
		return PTR_ERR(lamp_dev);
	}

	dev_info(lamp_dev, "ready at /sys/class/lamp/lamp0/\n");
	return 0;
}

static void __exit lamp_exit(void)
{
	device_unregister(lamp_dev);        /* спершу пристрій */
	class_unregister(&lamp_class);      /* потім клас, у якому він жив */
}

module_init(lamp_init);
module_exit(lamp_exit);

MODULE_DESCRIPTION("One-attribute example device for /sys/class");
MODULE_LICENSE("GPL");
