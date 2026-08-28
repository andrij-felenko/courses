arw_verdict arw_update(arw *w, uint32_t seq)
{
    if (!w->started) {                    /* перша датаграма задає точку відліку */
        w->started  = 1;
        w->top      = seq;
        w->first    = seq;
        w->bits     = 1;
        w->accepted = 1;
        return ARW_NEW;
    }

    int64_t d = seq_ahead(seq, w->top);

    if (d > 0) {                          /* новіша: вікно їде вперед на d позицій */
        unsigned live = arw_live(w);
        if (d < ARW_BITS) {
            unsigned stay   = ARW_BITS - (unsigned)d;   /* позицій лишається у вікні */
            uint64_t fallen = w->bits >> stay;          /* зсув 1..63 — законний */
            unsigned real   = live > stay ? live - stay : 0;
            w->lost += real - (unsigned)arw_popcount64(fallen);
            w->bits <<= (unsigned)d;                    /* зсув 1..63 — законний */
            w->bits |= 1;
        } else {
            /* Стрибок ширший за вікно: старий вміст виїхав цілком, а ще
               d − 64 номерів проскочили вікно наскрізь.
               Зсув на 64 і більше в C — невизначена поведінка, тож не зсуваємо. */
            w->lost += (live - (unsigned)arw_popcount64(w->bits))
                     + ((uint64_t)d - ARW_BITS);
            w->bits  = 1;
        }
        w->top = seq;
        w->accepted++;
        return ARW_NEW;
    }

    if (d <= -(int64_t)ARW_BITS) {        /* позаду вікна — пам'яті вже не лишилося */
        w->too_old++;
        return ARW_TOO_OLD;
    }

    unsigned k   = (unsigned)(-d);        /* 0..63 — відстань позаду top */
    uint64_t bit = (uint64_t)1 << k;      /* k ≤ 63 — законний зсув */

    if (w->bits & bit) {
        w->duplicate++;
        return ARW_DUPLICATE;
    }

    if (k >= arw_live(w))                 /* номер із-перед нашого старту */
        w->first = seq;
    w->bits |= bit;
    w->accepted++;
    w->reordered++;
    return ARW_LATE;
}
