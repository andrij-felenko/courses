static int hits_handler(const struct ctl_table *table, int write,
			void *buffer, size_t *lenp, loff_t *ppos)
{
	struct ctl_table tmp = *table;
	struct bins *b;
	int sum = 0, i;

	if (write)
		return -EACCES;

	rcu_read_lock();
	b = rcu_dereference(cur_bins);
	for (i = 0; i < b->n; i++)
		sum += atomic_read(&b->hit[i]);
	rcu_read_unlock();

	tmp.data = &sum;
	return proc_dointvec(&tmp, 0, buffer, lenp, ppos);
}
