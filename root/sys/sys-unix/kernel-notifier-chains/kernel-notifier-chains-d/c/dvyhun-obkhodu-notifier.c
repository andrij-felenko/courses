int notifier_call_chain(struct notifier_block **nl,
                        unsigned long val, void *v,
                        int nr_to_call, int *nr_calls)
{
    int ret = NOTIFY_DONE;
    struct notifier_block *nb, *next_nb;

    nb = rcu_dereference_raw(*nl);
    while (nb && nr_to_call) {
        next_nb = rcu_dereference_raw(nb->next);

        ret = nb->notifier_call(nb, val, v);

        if (nr_calls)
            (*nr_calls)++;

        if (ret & NOTIFY_STOP_MASK)
            break;

        nb = next_nb;
        nr_to_call--;
    }
    return ret;
}
