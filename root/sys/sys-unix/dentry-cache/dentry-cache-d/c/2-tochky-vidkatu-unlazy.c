/* Спроба перевести шлях з RCU-walk у звичайне володіння посиланнями */
static int unlazy_walk(struct nameidata *nd, struct dentry *dentry, unsigned seq)
{
    struct mount *mnt = nd->path.mnt;

    /* 1. Атомарно збільшуємо лічильники посилань mnt та dentry */
    if (!legitimize_path(nd, &nd->path, seq))
        goto out_drop;

    /* 2. Виходимо з критичної секції RCU */
    rcu_read_unlock();
    return 0;

out_drop:
    rcu_read_unlock();
    return -ECHILD; /* Збій: перезапустити весь обхід у Ref-walk від самого початку */
}
