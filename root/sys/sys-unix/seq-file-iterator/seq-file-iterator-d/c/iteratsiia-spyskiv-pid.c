static void *dev_seq_start(struct seq_file *m, loff_t *pos)
{
    /* 1. Входимо в критичну секцію читача RCU */
    rcu_read_lock();

    /* 2. Шукаємо вузол за логічним індексом */
    return seq_list_start_rcu(&device_list_head, *pos);
}

static void *dev_seq_next(struct seq_file *m, void *v, loff_t *pos)
{
    /* 3. Переходимо до наступного елемента списку */
    return seq_list_next_rcu(v, &device_list_head, pos);
}

static void dev_seq_stop(struct seq_file *m, void *v)
{
    /* 4. Завжди виходимо з критичної секції RCU */
    rcu_read_unlock();
}
