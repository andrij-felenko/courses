static bool mirror_invalidate(struct mmu_interval_notifier *sub,
                              const struct mmu_notifier_range *range,
                              unsigned long cur_seq)
{
        struct mirror *m = container_of(sub, struct mirror, sub);

        if (mmu_notifier_range_blockable(range))
                mutex_lock(&m->lock);
        else if (!mutex_trylock(&m->lock))
                return false;           /* нагору піде -EAGAIN */

        mmu_interval_set_seq(sub, cur_seq);
        mirror_drop_device_entries(m, range->start, range->end);

        mutex_unlock(&m->lock);
        return true;
}
