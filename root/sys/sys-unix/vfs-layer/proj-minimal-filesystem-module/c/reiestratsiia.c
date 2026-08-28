static int __init tiny_init(void)
{
	return register_filesystem(&tiny_fs_type);
}

static void __exit tiny_exit(void)
{
	unregister_filesystem(&tiny_fs_type);
}

module_init(tiny_init);
module_exit(tiny_exit);

MODULE_DESCRIPTION("tinyfs: a minimal mountable filesystem");
MODULE_AUTHOR("nobody");
MODULE_LICENSE("GPL");
