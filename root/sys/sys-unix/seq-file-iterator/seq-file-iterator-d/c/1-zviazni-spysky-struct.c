static void *dev_seq_start(struct seq_file *m, loff_t *pos)
{
    rcu_read_lock();
    return seq_list_start_rcu(&device_list_head, *pos);
}

static void *dev_seq_next(struct seq_file *m, void *v, loff_t *pos)
{
    return seq_list_next_rcu(v, &device_list_head, pos);
}
