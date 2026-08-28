static struct ctl_table knobdemo_table[] = {
	{
		.procname	= "interval_ms",
		.data		= &interval_ms,
		.maxlen		= sizeof(int),
		.mode		= 0644,
		.proc_handler	= proc_dointvec_minmax,
		.extra1		= &interval_min,
		.extra2		= &interval_max,
	},
	{
		.procname	= "slots",
		.data		= &slots,
		.maxlen		= sizeof(int),
		.mode		= 0644,
		.proc_handler	= slots_handler,
		.extra1		= &slots_min,
		.extra2		= &slots_max,
	},
	{
		.procname	= "hits",
		.maxlen		= sizeof(int),
		.mode		= 0444,
		.proc_handler	= hits_handler,
	},
};

static struct ctl_table_header *knobdemo_hdr;

static int __init knobdemo_init(void)
{
	struct bins *b = bins_alloc(slots);

	if (!b)
		return -ENOMEM;
	rcu_assign_pointer(cur_bins, b);

	knobdemo_hdr = register_sysctl("kernel/knobdemo", knobdemo_table);
	if (!knobdemo_hdr) {
		kvfree(b);
		return -ENOMEM;
	}

	INIT_DELAYED_WORK(&tick_work, tick_fn);
	schedule_delayed_work(&tick_work, msecs_to_jiffies(interval_ms));
	return 0;
}

static void __exit knobdemo_exit(void)
{
	unregister_sysctl_table(knobdemo_hdr);	/* чекає на обробники в роботі */
	cancel_delayed_work_sync(&tick_work);	/* і на відлік у роботі теж */
	kvfree(rcu_dereference_protected(cur_bins, true));
}

module_init(knobdemo_init);
module_exit(knobdemo_exit);
MODULE_DESCRIPTION("Демонстраційні параметри в /proc/sys/kernel/knobdemo");
MODULE_LICENSE("GPL");
