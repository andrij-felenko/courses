static int mirror_fault(struct mirror *m, unsigned long addr, unsigned long len)
{
        unsigned long seq;
        int ret;

        while (true) {
                seq = mmu_interval_read_begin(&m->sub);
                m->range.notifier_seq = seq;

                mmap_read_lock(m->mm);
                ret = hmm_range_fault(&m->range);
                mmap_read_unlock(m->mm);
                if (ret == -EBUSY)
                        continue;       /* зміна саме триває */
                if (ret)
                        return ret;

                mutex_lock(&m->lock);
                if (mmu_interval_read_retry(&m->sub, seq)) {
                        mutex_unlock(&m->lock);
                        continue;       /* хтось зняв ці сторінки — усе спочатку */
                }
                mirror_install_device_entries(m, addr, len);
                mutex_unlock(&m->lock);
                return 0;
        }
}
