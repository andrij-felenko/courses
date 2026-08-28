static const struct super_operations tiny_super_ops = {
	.statfs		= simple_statfs,
};

static int tiny_fill_super(struct super_block *sb, struct fs_context *fc)
{
	struct inode *root;

	sb->s_magic		= TINY_MAGIC;
	sb->s_op		= &tiny_super_ops;
	sb->s_blocksize		= PAGE_SIZE;
	sb->s_blocksize_bits	= PAGE_SHIFT;
	sb->s_maxbytes		= MAX_LFS_FILESIZE;
	sb->s_time_gran		= 1;

	root = tiny_make_inode(sb, S_IFDIR | 0555);
	if (!root)
		return -ENOMEM;

	/* d_make_root сама зробить iput() на невдачі — другий раз не звільняємо. */
	sb->s_root = d_make_root(root);
	if (!sb->s_root)
		return -ENOMEM;

	return 0;
}

static int tiny_get_tree(struct fs_context *fc)
{
	return get_tree_nodev(fc, tiny_fill_super);
}

static const struct fs_context_operations tiny_context_ops = {
	.get_tree	= tiny_get_tree,
};

static int tiny_init_fs_context(struct fs_context *fc)
{
	fc->ops = &tiny_context_ops;
	return 0;
}

static struct file_system_type tiny_fs_type = {
	.owner			= THIS_MODULE,
	.name			= "tinyfs",
	.init_fs_context	= tiny_init_fs_context,
	.kill_sb		= kill_anon_super,
};
MODULE_ALIAS_FS("tinyfs");
