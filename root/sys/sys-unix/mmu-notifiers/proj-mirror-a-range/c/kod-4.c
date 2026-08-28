static long mirror_attach(struct mirror *m, unsigned long start, unsigned long len)
{
        struct mm_struct *mm = current->mm;
        int ret;

        if (m->attached)
                return -EBUSY;
        if (!len || !IS_ALIGNED(start, PAGE_SIZE) || !IS_ALIGNED(len, PAGE_SIZE) ||
            (len >> PAGE_SHIFT) > MIRROR_MAX_PAGES)
                return -EINVAL;

        m->npages = len >> PAGE_SHIFT;
        m->start = start;
        m->dev_pte = kvcalloc(m->npages, sizeof(*m->dev_pte), GFP_KERNEL);
        m->pfns = kvcalloc(m->npages, sizeof(*m->pfns), GFP_KERNEL);
        if (!m->dev_pte || !m->pfns) {
                ret = -ENOMEM;
                goto err_free;
        }

        mmgrab(mm);             /* тримаємо СТРУКТУРУ, а не адресний простір */
        m->mm = mm;

        /* ⚠️ жодного m->lock тут: insert бере mmap_lock на запис */
        ret = mmu_interval_notifier_insert(&m->notifier, mm, start, len,
                                           &mirror_ops);
        if (ret)
                goto err_drop;

        m->attached = true;
        return 0;

err_drop:
        mmdrop(mm);
        m->mm = NULL;
err_free:
        kvfree(m->dev_pte);
        kvfree(m->pfns);
        m->dev_pte = m->pfns = NULL;
        return ret;
}

static int mirror_release(struct inode *inode, struct file *file)
{
        struct mirror *m = file->private_data;

        if (m->attached) {
                mmu_interval_notifier_remove(&m->notifier);
                /* після повернення зворотних викликів немає й не буде */
                mmdrop(m->mm);
        }
        kvfree(m->dev_pte);
        kvfree(m->pfns);
        kfree(m);
        return 0;
}
