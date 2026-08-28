/* Знімок робимо на відкритті, а не на читанні: між двома read() текст
 * не мусить мінятися, інакше другий виклик дістане обрізаний хвіст. */
static int tiny_open(struct inode *inode, struct file *file)
{
	char *buf;

	buf = kmalloc(TINY_BUFSZ, GFP_KERNEL);
	if (!buf)
		return -ENOMEM;

	scnprintf(buf, TINY_BUFSZ,
		  "uptime  %lld s\n"
		  "opens   %d\n"
		  "magic   0x%lx\n",
		  ktime_get_boottime_seconds(),
		  atomic_inc_return(&tiny_opens),
		  inode->i_sb->s_magic);

	file->private_data = buf;
	return 0;
}

static ssize_t tiny_read(struct file *file, char __user *to,
			 size_t count, loff_t *ppos)
{
	const char *buf = file->private_data;

	return simple_read_from_buffer(to, count, ppos, buf, strlen(buf));
}

static int tiny_release(struct inode *inode, struct file *file)
{
	kfree(file->private_data);
	return 0;
}

static const struct file_operations tiny_file_ops = {
	.owner		= THIS_MODULE,
	.open		= tiny_open,
	.read		= tiny_read,
	.release	= tiny_release,
	.llseek		= default_llseek,
};
