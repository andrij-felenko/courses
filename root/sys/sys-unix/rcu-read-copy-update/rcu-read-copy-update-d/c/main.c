/* читач: жодного спільного запису на всьому шляху */
rcu_read_lock();
list_for_each_entry_rcu(d, &dev_list, node) {
    if (d->ifindex == idx) {
        found = d;
        break;
    }
}
/* усе, що робимо з found, робимо ТУТ, до розблокування */
rcu_read_unlock();

/* письменник: між письменниками — звичайний замок */
mutex_lock(&dev_mutex);
list_del_rcu(&d->node);
mutex_unlock(&dev_mutex);
call_rcu(&d->rcu, dev_free);   /* звільнити після періоду відстрочки */
