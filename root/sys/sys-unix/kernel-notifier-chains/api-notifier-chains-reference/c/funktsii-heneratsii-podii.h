int atomic_notifier_call_chain(struct atomic_notifier_head *nh,
                               unsigned long val, void *v);

int blocking_notifier_call_chain(struct blocking_notifier_head *nh,
                                 unsigned long val, void *v);

int raw_notifier_call_chain(struct raw_notifier_head *nh,
                            unsigned long val, void *v);

int srcu_notifier_call_chain(struct srcu_notifier_head *nh,
                             unsigned long val, void *v);
