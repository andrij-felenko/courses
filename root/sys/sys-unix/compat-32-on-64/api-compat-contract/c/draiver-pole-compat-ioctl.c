/* uapi-заголовок драйвера */
struct widget_cfg {
	__u32		channel;
	__u32		_pad;		/* явна набивка до межі 8 */
	__aligned_u64	window_ns;	/* вирівнювання 8 в ОБОХ ABI */
};

#define WIDGET_SET_CFG _IOW('W', 1, struct widget_cfg)

/* драйвер */
static long widget_ioctl(struct file *f, unsigned int cmd, unsigned long arg)
{
	struct widget_cfg cfg;

	if (cmd != WIDGET_SET_CFG)
		return -ENOTTY;
	if (copy_from_user(&cfg, (void __user *)arg, sizeof(cfg)))
		return -EFAULT;
	if (cfg._pad)			/* набивка мусить бути нульова */
		return -EINVAL;

	return widget_apply(&cfg);
}

static const struct file_operations widget_fops = {
	.owner		= THIS_MODULE,
	.unlocked_ioctl	= widget_ioctl,
	.compat_ioctl	= compat_ptr_ioctl,
};
