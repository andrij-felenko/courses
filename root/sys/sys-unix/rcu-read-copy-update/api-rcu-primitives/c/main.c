struct dev_entry {
    struct list_head node;
    struct rcu_head  rcu;
    int              ifindex;
    char             name[16];
};

static LIST_HEAD(dev_list);
static DEFINE_MUTEX(dev_mutex);            /* лише між письменниками */

/* читач: жодного спільного запису на всьому шляху */
static int dev_name_of(int ifindex, char *out, size_t n)
{
    struct dev_entry *d;
    int ret = -ENODEV;

    rcu_read_lock();
    list_for_each_entry_rcu(d, &dev_list, node) {
        if (d->ifindex == ifindex) {
            strscpy(out, d->name, n);      /* копіюємо ТУТ, поки вузол живий */
            ret = 0;
            break;
        }
    }
    rcu_read_unlock();
    return ret;                            /* d назовні вже недійсний */
}

/* зворотний виклик: спати тут не можна */
static void dev_free(struct rcu_head *head)
{
    kfree(container_of(head, struct dev_entry, rcu));
}

static void dev_remove(int ifindex)
{
    struct dev_entry *d;

    mutex_lock(&dev_mutex);
    list_for_each_entry(d, &dev_list, node) {   /* під замком — звичайний обхід */
        if (d->ifindex == ifindex) {
            list_del_rcu(&d->node);
            mutex_unlock(&dev_mutex);
            call_rcu(&d->rcu, dev_free);
            return;
        }
    }
    mutex_unlock(&dev_mutex);
}

static void __exit dev_exit(void)
{
    rcu_barrier();      /* інакше dev_free зникне разом із модулем */
}
