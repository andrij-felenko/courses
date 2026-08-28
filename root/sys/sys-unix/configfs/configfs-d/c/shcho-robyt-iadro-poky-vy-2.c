static ssize_t my_limit_show(struct config_item *item, char *page)
{
	return sysfs_emit(page, "%u\n", to_my_target(item)->limit);
}

static ssize_t my_limit_store(struct config_item *item,
			      const char *page, size_t count)
{
	unsigned int v;
	int ret = kstrtouint(page, 0, &v);

	if (ret)
		return ret;
	if (v > 1024)
		return -ERANGE;
	to_my_target(item)->limit = v;
	return count;
}
CONFIGFS_ATTR(my_, limit);
