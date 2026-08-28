static void demo_target_release(struct config_item *item)
{
	kfree(to_demo_target(item));	/* єдине місце, де звільняють */
}

static const struct configfs_item_operations demo_target_item_ops = {
	.release = demo_target_release,
};

static const struct config_item_type demo_target_type = {
	.ct_item_ops	= &demo_target_item_ops,
	.ct_attrs	= demo_target_attrs,
	.ct_owner	= THIS_MODULE,
};

/* ── підоб'єкт t1/slots/s0 ─────────────────────────────────────────── */

static ssize_t demo_slot_weight_show(struct config_item *item, char *page)
{
	return sysfs_emit(page, "%u\n", to_demo_slot(item)->weight);
}

static ssize_t demo_slot_weight_store(struct config_item *item,
				      const char *page, size_t count)
{
	int ret = kstrtouint(page, 0, &to_demo_slot(item)->weight);

	return ret ? ret : count;
}
CONFIGFS_ATTR(demo_slot_, weight);

static struct configfs_attribute *demo_slot_attrs[] = {
	&demo_slot_attr_weight,
	NULL,
};

static void demo_slot_release(struct config_item *item)
{
	kfree(to_demo_slot(item));
}

static const struct configfs_item_operations demo_slot_item_ops = {
	.release = demo_slot_release,
};

static const struct config_item_type demo_slot_type = {
	.ct_item_ops	= &demo_slot_item_ops,
	.ct_attrs	= demo_slot_attrs,
	.ct_owner	= THIS_MODULE,
};

/* ── типова група t1/slots/ ────────────────────────────────────────── */

static struct config_item *demo_slots_make_item(struct config_group *group,
						const char *name)
{
	struct demo_slot *slot;

	if (strlen(name) > 8)
		return ERR_PTR(-ENAMETOOLONG);	/* NULL тут став би -ENOMEM */

	slot = kzalloc(sizeof(*slot), GFP_KERNEL);
	if (!slot)
		return ERR_PTR(-ENOMEM);

	config_item_init_type_name(&slot->item, name, &demo_slot_type);
	return &slot->item;
}

static void demo_slots_drop_item(struct config_group *group,
				 struct config_item *item)
{
	config_item_put(item);		/* не kfree: звільнить release() */
}

static int demo_slots_allow_link(struct config_item *src,
				 struct config_item *target)
{
	struct demo_target *self = slots_to_target(src);

	if (target->ci_type != &demo_target_type)
		return -EINVAL;		/* посилатися можна лише на об'єкт demo/ */
	if (target == &self->group.cg_item)
		return -ELOOP;		/* сам на себе — ні */
	if (self->nr_links >= 4)
		return -ENOSPC;

	self->nr_links++;
	return 0;
}

static void demo_slots_drop_link(struct config_item *src,
				 struct config_item *target)
{
	slots_to_target(src)->nr_links--;
}

static const struct configfs_item_operations demo_slots_item_ops = {
	.allow_link	= demo_slots_allow_link,
	.drop_link	= demo_slots_drop_link,
};

static const struct configfs_group_operations demo_slots_group_ops = {
	.make_item	= demo_slots_make_item,
	.drop_item	= demo_slots_drop_item,
};

static const struct config_item_type demo_slots_type = {
	.ct_item_ops	= &demo_slots_item_ops,
	.ct_group_ops	= &demo_slots_group_ops,
	.ct_owner	= THIS_MODULE,
};
