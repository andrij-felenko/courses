static void pdev_name_broken(unsigned int id)
{
    struct pdev *p, *found = NULL;

    rcu_read_lock();
    list_for_each_entry_rcu(p, &pdev_list, node)
        if (p->id == id) {
            found = p;
            break;
        }
    rcu_read_unlock();

    if (found)
        pr_info("rcudemo: %u = %s\n", id, found->name);   /* ✗ звільнена пам'ять */
}
