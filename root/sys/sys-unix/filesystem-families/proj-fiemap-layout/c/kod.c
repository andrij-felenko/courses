struct walk {
    uint64_t n;                 /* екстентів у карті                     */
    uint64_t mapped;            /* сума fe_length                        */
    uint64_t longest;
    uint64_t holes, hole_bytes;
    uint64_t unwritten, delalloc, shared, encoded;
    uint64_t pairs, glued;      /* сусідніх пар / з них — упритул        */

    uint64_t seen_end;          /* найбільший побачений логічний кінець  */
    int have_prev;
    struct fiemap_extent prev;
};

/* записи, на яких фізичну арифметику робити не можна:
   місця ще немає (UNKNOWN, DELALLOC), зсув не кратний блокові (NOT_ALIGNED)
   або довжина виміряна не в тих одиницях, що займане місце (ENCODED) */
#define VAGUE (FIEMAP_EXTENT_UNKNOWN | FIEMAP_EXTENT_DELALLOC | \
               FIEMAP_EXTENT_NOT_ALIGNED | FIEMAP_EXTENT_ENCODED)

static void take(struct walk *w, const struct fiemap_extent *e, int verbose, uint64_t idx)
{
    if (e->fe_logical + e->fe_length <= w->seen_end)
        return;                                   /* цей запис ми вже бачили */

    if (e->fe_logical > w->seen_end) {            /* між даними — діра */
        w->holes++;
        w->hole_bytes += e->fe_logical - w->seen_end;
    }

    w->n++;
    w->mapped += e->fe_length;
    if (e->fe_length > w->longest)
        w->longest = e->fe_length;
    if (e->fe_flags & FIEMAP_EXTENT_UNWRITTEN) w->unwritten += e->fe_length;
    if (e->fe_flags & FIEMAP_EXTENT_DELALLOC)  w->delalloc  += e->fe_length;
    if (e->fe_flags & FIEMAP_EXTENT_SHARED)    w->shared    += e->fe_length;
    if (e->fe_flags & FIEMAP_EXTENT_ENCODED)   w->encoded   += e->fe_length;

    if (w->have_prev && !((w->prev.fe_flags | e->fe_flags) & VAGUE)) {
        w->pairs++;
        if (w->prev.fe_physical + w->prev.fe_length == e->fe_physical &&
            w->prev.fe_logical  + w->prev.fe_length == e->fe_logical)
            w->glued++;                           /* сусіди стик у стик */
    }

    if (verbose) {
        char fs[160];
        flags_str(e->fe_flags, fs, sizeof fs);
        printf("%8" PRIu64 " %14" PRIu64 " %12" PRIu64 " %16" PRIu64 "  %s\n",
               idx, (uint64_t)e->fe_logical, (uint64_t)e->fe_length,
               (uint64_t)e->fe_physical, fs);
    }

    w->seen_end = e->fe_logical + e->fe_length;
    w->prev = *e;
    w->have_prev = 1;
}
