static void __exit rcudemo_exit(void)
{
    struct pdev *p, *tmp;

    proc_remove(entry);        /* 1. нових звертань більше не буде */

    mutex_lock(&pdev_mutex);   /* 2. спорожнити список */
    list_for_each_entry_safe(p, tmp, &pdev_list, node) {
        list_del_rcu(&p->node);
        call_rcu(&p->rcu, pdev_free_rcu);
    }
    mutex_unlock(&pdev_mutex);

    rcu_barrier();             /* 3. дочекатися ВЛАСНИХ зворотних викликів */
}
