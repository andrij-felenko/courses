static int slots_handler(const struct ctl_table *table, int write,
			 void *buffer, size_t *lenp, loff_t *ppos)
{
	struct bins *old, *new;
	int prev, ret;

	mutex_lock(&bins_lock);

	prev = slots;
	ret = proc_dointvec_minmax(table, write, buffer, lenp, ppos);
	if (ret || !write || slots == prev)
		goto out;			/* читання або те саме число */

	new = bins_alloc(slots);
	if (!new) {
		WRITE_ONCE(slots, prev);	/* не показувати того, чого не зробили */
		ret = -ENOMEM;
		goto out;
	}

	old = rcu_dereference_protected(cur_bins, lockdep_is_held(&bins_lock));
	rcu_assign_pointer(cur_bins, new);
	WRITE_ONCE(rebuilds, rebuilds + 1);
	kvfree_rcu(old, rcu);

	pr_info("slots %d -> %d (rebuild %d)\n", prev, new->n, rebuilds);
out:
	mutex_unlock(&bins_lock);
	return ret;
}
