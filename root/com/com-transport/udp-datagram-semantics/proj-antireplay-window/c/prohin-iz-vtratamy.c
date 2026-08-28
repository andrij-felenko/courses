/* Визнати втраченими всі номери, що досі висять у вікні нулями.
   Викликати РІВНО ОДИН раз, коли потік завершено. */
uint64_t arw_flush(arw *w)
{
    if (!w->started) return 0;
    unsigned live = arw_live(w);
    /* зсув на 64 — та сама невизначена поведінка, тому окрема гілка */
    uint64_t mask = (live >= ARW_BITS) ? ~(uint64_t)0
                                       : (((uint64_t)1 << live) - 1);
    uint64_t pending = live - (uint64_t)arw_popcount64(w->bits & mask);
    w->lost += pending;
    return pending;
}
