typedef struct {
    unsigned reg[S];      /* D-бітний декодований префікс на стан; біт D−1 — найдавніший */
    int      metric[S];
    int      t;
} rx_smu;

static void rx_init(rx_smu *q) {
    q->t = 0;
    q->metric[0] = 0;
    for (unsigned s = 1; s < S; s++) q->metric[s] = INT_MAX;
    for (unsigned s = 0; s < S; s++) q->reg[s] = 0;
}

static int rx_step(rx_smu *q, int r0, int r1, int *out) {
    int nm[S];
    unsigned nreg[S];
    for (unsigned d = 0; d < S; d++) { nm[d] = INT_MAX; nreg[d] = 0; }
    for (unsigned s = 0; s < S; s++) {
        if (q->metric[s] == INT_MAX) continue;
        for (int u = 0; u < 2; u++) {
            unsigned ns   = (unsigned) NXT[s][u];
            int      cand = q->metric[s] + hamm(OUT[s][u], r0, r1);
            if (cand < nm[ns]) {
                nm[ns] = cand;
                unsigned unew = ns >> (NU - 1);                    /* вхідний біт ребра s→ns */
                nreg[ns] = ((q->reg[s] << 1) | unew) & ((1u << D) - 1);  /* копія + зсув */
            }
        }
    }
    memcpy(q->metric, nm, sizeof nm);
    memcpy(q->reg,    nreg, sizeof nreg);             /* УСЯ пам'ять переписана щотакту */
    q->t++;
    if (q->t < D) return 0;
    *out = (int)((q->reg[best(q->metric)] >> (D - 1)) & 1u);   /* найстарший біт — миттєво */
    return 1;
}
