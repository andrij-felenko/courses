static uint32_t rng;
static uint32_t rnd(void)                     /* xorshift32, щоб прогін   */
{                                             /* відтворювався точно      */
    uint32_t x = rng;
    x ^= x << 13; x ^= x >> 17; x ^= x << 5;
    return rng = x;
}

static void step(void)
{
    int32_t ino, off;
    ensure_free();
    if (rnd() % 100 < 90) ino = (int32_t)(rnd() % (uint32_t)nhot);
    else ino = nhot + (int32_t)(rnd() % (uint32_t)(nfiles - nhot));
    off = (int32_t)(rnd() % FILE_BLOCKS);
    file_write(ino, off);
}

static void run(int pol, int sep, double rho)
{
    int32_t s, ino, off;
    long    k;

    policy = pol; sep_head = sep;
    nfiles = (int32_t)(rho * NSEGS);          /* файл завбільшки з сегмент */
    nhot   = nfiles / 10; if (nhot < 1) nhot = 1;
    for (s = 0; s < NSEGS; s++) {
        seg[s].is_free = 1; seg[s].written = 0;
        seg[s].live = 0;    seg[s].sealed  = 0;
    }
    for (ino = 0; ino < nfiles; ino++)
        for (off = 0; off < FILE_BLOCKS; off++) inode[ino][off] = -1;
    free_segs = NSEGS; head[0] = head[1] = -1; now_ = 0; rng = 2463534242u;

    /* 1. заповнення: файли ростуть упереміш, а не один за одним */
    for (off = 0; off < FILE_BLOCKS; off++)
        for (ino = 0; ino < nfiles; ino++) { ensure_free(); file_write(ino, off); }

    /* 2. розігрів: вибиваємо початкову розкладку, доходимо до сталого режиму */
    for (k = 0; k < WARMUP; k++) step();

    /* 3. вимірювання зі свіжими лічильниками */
    user_writes = clean_writes = clean_reads = victims = stalls = 0;
    u_sum = 0.0;
    for (k = 0; k < MEASURE; k++) step();
}

int main(void)
{
    static const double rhos[] = { 0.50, 0.70, 0.80, 0.90, 0.95 };
    static const struct { int pol, sep; const char *name; } var[] = {
        { GREEDY,  1, "greedy"         },
        { COSTBEN, 1, "cost-benefit"   },
        { COSTBEN, 0, "cost-ben 1head" }
    };
    int r, v;

    printf("  rho  policy           u_vict  WA_write  WA_total  2/(1-u)  stall\n");
    for (r = 0; r < 5; r++)
        for (v = 0; v < 3; v++) {
            double ub, wa_w, wa_t;
            run(var[v].pol, var[v].sep, rhos[r]);
            if (user_writes == 0) {
                printf(" %.2f  %-15s   том став: прибирачеві нема куди писати\n",
                       rhos[r], var[v].name);
                continue;
            }
            ub   = victims ? u_sum / (double)victims : 0.0;
            wa_w = (double)(user_writes + clean_writes) / (double)user_writes;
            wa_t = (double)(user_writes + clean_writes + clean_reads)
                   / (double)user_writes;
            printf(" %.2f  %-15s  %6.3f  %8.2f  %8.2f  %7.2f  %5lld\n",
                   rhos[r], var[v].name, ub, wa_w, wa_t,
                   2.0 / (1.0 - ub), stalls);
        }
    return 0;
}
