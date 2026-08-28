static struct config_group *demo_make_group(struct config_group *group,
					    const char *name)
{
	struct demo_target *t;

	t = kzalloc(sizeof(*t), GFP_KERNEL);
	if (!t)
		return ERR_PTR(-ENOMEM);

	t->limit = 1;
	strscpy(t->label, "unnamed", sizeof(t->label));

	config_group_init_type_name(&t->group, name, &demo_target_type);
	config_group_init_type_name(&t->slots, "slots", &demo_slots_type);
	configfs_add_default_group(&t->slots, &t->group);

	return &t->group;
}

static void demo_drop_item(struct config_group *group,
			   struct config_item *item)
{
	config_item_put(item);
}

static const struct configfs_group_operations demo_root_group_ops = {
	.make_group	= demo_make_group,
	.drop_item	= demo_drop_item,
};

static const struct config_item_type demo_root_type = {
	.ct_group_ops	= &demo_root_group_ops,
	.ct_owner	= THIS_MODULE,
};

static struct configfs_subsystem demo_subsys = {
	.su_group = {
		.cg_item = {
			.ci_namebuf	= "demo",
			.ci_type	= &demo_root_type,
		},
	},
};

static int __init demo_init(void)
{
	int ret;

	config_group_init(&demo_subsys.su_group);
	mutex_init(&demo_subsys.su_mutex);

	ret = configfs_register_subsystem(&demo_subsys);
	if (ret)
		pr_err("configfs_demo: реєстрація не вдалася: %d\n", ret);

	return ret;
}

static void __exit demo_exit(void)
{
	configfs_unregister_subsystem(&demo_subsys);
}

module_init(demo_init);
module_exit(demo_exit);
MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("Мінімальне піддерево configfs");
