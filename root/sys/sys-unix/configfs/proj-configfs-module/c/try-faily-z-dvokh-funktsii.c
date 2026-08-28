static ssize_t demo_target_limit_show(struct config_item *item, char *page)
{
	return sysfs_emit(page, "%u\n", to_demo_target(item)->limit);
}

static ssize_t demo_target_limit_store(struct config_item *item,
				       const char *page, size_t count)
{
	unsigned int v;
	int ret;

	ret = kstrtouint(page, 0, &v);	/* "abc" → -EINVAL, завелике → -ERANGE */
	if (ret)
		return ret;
	if (v > DEMO_LIMIT_MAX)
		return -ERANGE;

	to_demo_target(item)->limit = v;
	return count;			/* саме count, не 0 і не менше */
}
CONFIGFS_ATTR(demo_target_, limit);

static ssize_t demo_target_label_show(struct config_item *item, char *page)
{
	return sysfs_emit(page, "%s\n", to_demo_target(item)->label);
}

static ssize_t demo_target_label_store(struct config_item *item,
				       const char *page, size_t count)
{
	struct demo_target *t = to_demo_target(item);
	size_t len = count;

	while (len && (page[len - 1] == '\n' || page[len - 1] == '\r'))
		len--;			/* echo додає переведення рядка */
	if (len >= sizeof(t->label))
		return -ENAMETOOLONG;

	memcpy(t->label, page, len);
	t->label[len] = '\0';
	return count;
}
CONFIGFS_ATTR(demo_target_, label);

static ssize_t demo_target_nr_links_show(struct config_item *item, char *page)
{
	return sysfs_emit(page, "%u\n", to_demo_target(item)->nr_links);
}
CONFIGFS_ATTR_RO(demo_target_, nr_links);

static struct configfs_attribute *demo_target_attrs[] = {
	&demo_target_attr_limit,
	&demo_target_attr_label,
	&demo_target_attr_nr_links,
	NULL,
};
