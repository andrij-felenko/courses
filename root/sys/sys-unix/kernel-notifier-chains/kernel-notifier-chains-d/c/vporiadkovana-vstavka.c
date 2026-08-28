static int notifier_chain_register(struct notifier_block **nl,
                                  struct notifier_block *n)
{
    while ((*nl) != NULL) {
        if (unlikely((*nl) == n))
            return -EEXIST;
        if (n->priority > (*nl)->priority)
            break;
        nl = &((*nl)->next);
    }
    n->next = *nl;
    rcu_assign_pointer(*nl, n);
    return 0;
}
