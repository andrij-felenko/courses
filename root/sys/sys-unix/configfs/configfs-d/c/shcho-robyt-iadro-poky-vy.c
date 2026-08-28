struct my_target {
	struct config_item item;
	unsigned int limit;
};

static struct config_item *my_make_item(struct config_group *group,
					const char *name)
{
	struct my_target *t = kzalloc(sizeof(*t), GFP_KERNEL);

	if (!t)
		return ERR_PTR(-ENOMEM);
	config_item_init_type_name(&t->item, name, &my_item_type);
	return &t->item;
}
