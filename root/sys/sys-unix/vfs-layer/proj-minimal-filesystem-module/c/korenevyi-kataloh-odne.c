static struct inode *tiny_make_inode(struct super_block *sb, umode_t mode)
{
	struct inode *inode = new_inode(sb);

	if (!inode)
		return NULL;

	/* Власника ніде не записано — беремо того, хто звертається саме зараз:
	 * inode_init_owner() ставить current_fsuid()/current_fsgid(). */
	inode_init_owner(&nop_mnt_idmap, inode, NULL, mode);
	simple_inode_init_ts(inode);

	if (S_ISDIR(mode)) {
		inode->i_ino  = TINY_INO_ROOT;
		inode->i_op   = &tiny_dir_inode_ops;
		inode->i_fop  = &tiny_dir_ops;
		inc_nlink(inode);	/* каталог має щонайменше два імені: "." і своє */
	} else {
		inode->i_ino  = TINY_INO_FILE;
		inode->i_fop  = &tiny_file_ops;
		inode->i_size = 0;	/* справжнього розміру до генерації не знаємо */
	}
	return inode;
}

static int tiny_iterate(struct file *file, struct dir_context *ctx)
{
	if (!dir_emit_dots(file, ctx))
		return 0;

	if (ctx->pos == 2) {
		if (!dir_emit(ctx, TINY_NAME, sizeof(TINY_NAME) - 1,
			      TINY_INO_FILE, DT_REG))
			return 0;
		ctx->pos = 3;
	}
	return 0;
}

static struct dentry *tiny_lookup(struct inode *dir, struct dentry *dentry,
				  unsigned int flags)
{
	struct inode *inode = NULL;

	if (dentry->d_name.len == sizeof(TINY_NAME) - 1 &&
	    !memcmp(dentry->d_name.name, TINY_NAME, sizeof(TINY_NAME) - 1)) {
		inode = tiny_make_inode(dir->i_sb, S_IFREG | 0444);
		if (!inode)
			return ERR_PTR(-ENOMEM);
	}

	/* inode == NULL — це не помилка, а від'ємний запис: «імені тут немає». */
	return d_splice_alias(inode, dentry);
}

static const struct inode_operations tiny_dir_inode_ops = {
	.lookup		= tiny_lookup,
};

static const struct file_operations tiny_dir_ops = {
	.owner		= THIS_MODULE,
	.iterate_shared	= tiny_iterate,
	.read		= generic_read_dir,
	.llseek		= generic_file_llseek,
};
