int seq = 0;
again:
    /* seq парне — seqlock; seq непарне — захоплення спін-замка */
    read_seqbegin_or_lock(&my_seqlock, &seq);

    /* Зчитування полів даних */
    local_val1 = global_data.val1;
    local_val2 = global_data.val2;

    if (need_seqretry(&my_seqlock, seq)) {
        seq = 1;                        /* друга спроба — під замком */
        goto again;
    }

/* Завершення читання та звільнення замка (якщо він брався) */
done_seqretry(&my_seqlock, seq);
