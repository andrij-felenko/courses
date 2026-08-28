/* Читач: лише позначає межі, жодних блокувань */
rcu_read_lock();
list_for_each_entry_rcu(d, &dev_list, node) {
    if (d->ifindex == idx) {
        found = d;
        break;
    }
}
/* Робота з found має завершитися до unlock */
rcu_read_unlock();

/* Письменник (вилучення) */
mutex_lock(&dev_mutex); /* RCU не захищає письменників один від одного */
list_del_rcu(&d->node);
mutex_unlock(&dev_mutex);

/* Асинхронне звільнення після Grace Period */
call_rcu(&d->rcu, dev_free);
