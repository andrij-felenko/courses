static bool mirror_invalidate(struct mmu_interval_notifier *mni,
                              const struct mmu_notifier_range *range,
                              unsigned long cur_seq)
{
        struct mirror *m = container_of(mni, struct mirror, notifier);
        unsigned long first, last, addr;

        if (mmu_notifier_range_blockable(range))
                mutex_lock(&m->lock);
        else if (!mutex_trylock(&m->lock))
                return false;   /* тому, хто кликав, піде -EAGAIN */

        mmu_interval_set_seq(mni, cur_seq);

        first = max(range->start, m->start);
        last  = min(range->end, m->start + (m->npages << PAGE_SHIFT));
        for (addr = first; addr < last; addr += PAGE_SIZE)
                m->dev_pte[(addr - m->start) >> PAGE_SHIFT] = 0;

        mutex_unlock(&m->lock);
        return true;
}

static const struct mmu_interval_notifier_ops mirror_ops = {
        .invalidate = mirror_invalidate,
};
