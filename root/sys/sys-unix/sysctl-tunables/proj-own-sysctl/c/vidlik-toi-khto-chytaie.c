static void tick_fn(struct work_struct *w)
{
	struct bins *b;

	rcu_read_lock();
	b = rcu_dereference(cur_bins);
	atomic_inc(&b->hit[get_random_u32() % b->n]);
	rcu_read_unlock();

	schedule_delayed_work(&tick_work,
			      msecs_to_jiffies(READ_ONCE(interval_ms)));
}
