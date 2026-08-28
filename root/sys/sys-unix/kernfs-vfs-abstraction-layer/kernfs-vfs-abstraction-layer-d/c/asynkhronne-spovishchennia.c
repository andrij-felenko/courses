void kernfs_notify(struct kernfs_node *kn)
{
    struct kernfs_open_node *on;
    unsigned long flags;

    if (WARN_ON(kernfs_type(kn) != KERNFS_FILE))
        return;

    /* негайно копнути poll */
    spin_lock_irqsave(&kernfs_open_node_lock, flags);
    on = kn->attr.open;
    if (on) {
        atomic_inc(&on->event);
        wake_up_interruptible(&on->poll);
    }
    spin_unlock_irqrestore(&kernfs_open_node_lock, flags);

    /* далі — друга половина: вузол стає у список kernfs_notify_list
       і schedule_work() відкладає підняття fsnotify/inotify */
}
