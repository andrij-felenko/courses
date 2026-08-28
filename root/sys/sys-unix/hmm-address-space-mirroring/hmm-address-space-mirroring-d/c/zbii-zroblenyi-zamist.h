struct hmm_range range = {
        .notifier      = &mirror->sub,          /* вузол сповіщувача на цей діапазон */
        .start         = addr,
        .end           = addr + len,
        .hmm_pfns      = pfns,                  /* сюди ляжуть відповіді */
        .default_flags = HMM_PFN_REQ_FAULT,     /* політика на весь діапазон */
        .pfn_flags_mask = 0,                    /* окремі сторінки своїх вимог не мають */
};

mmap_read_lock(mm);
ret = hmm_range_fault(&range);
mmap_read_unlock(mm);
