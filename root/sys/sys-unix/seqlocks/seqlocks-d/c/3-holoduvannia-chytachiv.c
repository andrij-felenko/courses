int seq = 0;
again:
    /* seq парне — оптимістичне читання; seq непарне — захоплення spinlock */
    read_seqbegin_or_lock(&sl, &seq);

    local_data = global_data;

    if (need_seqretry(&sl, seq)) {
        seq = 1;                 /* друга спроба — вже під виключним замком */
        goto again;
    }
    done_seqretry(&sl, seq);     /* звільняє замок, якщо він брався */
