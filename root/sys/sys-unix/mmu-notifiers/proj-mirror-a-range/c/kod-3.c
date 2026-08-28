static int mirror_fault(struct mirror *m, unsigned long start, unsigned long len)
{
        unsigned long n = len >> PAGE_SHIFT;
        unsigned long base = (start - m->start) >> PAGE_SHIFT;
        struct hmm_range range = {
                .notifier      = &m->notifier,
                .start         = start,
                .end           = start + len,
                .hmm_pfns      = m->pfns,
                .default_flags = HMM_PFN_REQ_FAULT,
        };
        unsigned long i;
        int ret;

        if (!mmget_not_zero(m->mm))
                return -EFAULT;         /* адресного простору вже немає */

        for (;;) {
                range.notifier_seq = mmu_interval_read_begin(&m->notifier);

                mmap_read_lock(m->mm);
                ret = hmm_range_fault(&range);
                mmap_read_unlock(m->mm);
                if (ret) {
                        if (ret == -EBUSY)
                                continue;       /* зміна саме триває */
                        break;
                }

                mutex_lock(&m->lock);
                if (mmu_interval_read_retry(&m->notifier, range.notifier_seq)) {
                        mutex_unlock(&m->lock);
                        continue;               /* усе спочатку */
                }

                for (i = 0; i < n; i++)
                        m->dev_pte[base + i] = (m->pfns[i] & HMM_PFN_VALID) ?
                                page_to_pfn(hmm_pfn_to_page(m->pfns[i])) : 0;

                mutex_unlock(&m->lock);
                break;
        }

        mmput(m->mm);
        return ret;
}
