struct kernfs_node *kernfs_get_active(struct kernfs_node *kn)
{
    if (unlikely(!kn))
        return NULL;

    if (!atomic_inc_unless_negative(&kn->active))
        return NULL;

    if (kernfs_lockdep(kn))
        rwsem_acquire_read(&kn->dep_map, 0, 1, _RET_IP_);

    return kn;
}
