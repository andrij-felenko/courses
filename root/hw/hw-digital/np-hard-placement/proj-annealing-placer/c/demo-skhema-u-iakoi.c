/* Зі сполук-виводів побудувати зворотну таблицю «блок → його сполуки».
   Класична розкладка лічбою: порахувати, скласти зміщення, розкласти. */
static void build_incidence(Netlist *nl)
{
    int npins = nl->net_off[nl->nnets];

    nl->blk_off = calloc((size_t)nl->nblocks + 1, sizeof(int));
    for (int p = 0; p < npins; p++)
        nl->blk_off[nl->net_pins[p] + 1]++;
    for (int b = 0; b < nl->nblocks; b++)
        nl->blk_off[b + 1] += nl->blk_off[b];

    nl->blk_nets = malloc((size_t)npins * sizeof(int));
    int *fill = malloc((size_t)nl->nblocks * sizeof(int));
    memcpy(fill, nl->blk_off, (size_t)nl->nblocks * sizeof(int));
    for (int n = 0; n < nl->nnets; n++)
        for (int p = nl->net_off[n]; p < nl->net_off[n + 1]; p++)
            nl->blk_nets[fill[nl->net_pins[p]]++] = n;
    free(fill);
}

/* Демо-схема: блоки — вузли сітки W×H, сполуки — між сусідами.
   Найкраща розкладка відома НАПЕРЕД: блок i у слот i, кожна сполука
   завдовжки 1, HPWL = кількості сполук. Є з чим порівняти результат. */
static void make_mesh(Netlist *nl, int W, int H)
{
    nl->nblocks = W * H;
    nl->nnets   = (W - 1) * H + W * (H - 1);
    nl->net_off  = malloc((size_t)(nl->nnets + 1) * sizeof(int));
    nl->net_pins = malloc((size_t)(2 * nl->nnets) * sizeof(int));

    int n = 0, p = 0;
    for (int y = 0; y < H; y++)
        for (int x = 0; x < W; x++) {
            if (x + 1 < W) {                       /* сусід праворуч */
                nl->net_off[n++] = p;
                nl->net_pins[p++] = y * W + x;
                nl->net_pins[p++] = y * W + x + 1;
            }
            if (y + 1 < H) {                       /* сусід знизу */
                nl->net_off[n++] = p;
                nl->net_pins[p++] = y * W + x;
                nl->net_pins[p++] = (y + 1) * W + x;
            }
        }
    nl->net_off[n] = p;
    build_incidence(nl);
}

/* Випадковий старт: тасування Фішера–Єйтса по слотах. */
static void random_placement(Placement *pl, const Netlist *nl, const Grid *g)
{
    pl->blk_at  = malloc((size_t)g->nslots * sizeof(int));
    pl->slot_of = malloc((size_t)nl->nblocks * sizeof(int));
    int *perm   = malloc((size_t)g->nslots * sizeof(int));

    for (int s = 0; s < g->nslots; s++) perm[s] = s;
    for (int s = g->nslots - 1; s > 0; s--) {
        int j = rnd_below(s + 1);
        int t = perm[s]; perm[s] = perm[j]; perm[j] = t;
    }
    for (int s = 0; s < g->nslots; s++) pl->blk_at[s] = -1;
    for (int b = 0; b < nl->nblocks; b++) {
        pl->slot_of[b] = perm[b];
        pl->blk_at[perm[b]] = b;
    }
    free(perm);
}

int main(void)
{
    enum { SIDE = 16 };
    Grid g = { SIDE, SIDE, SIDE * SIDE };
    Netlist nl;
    Placement pl;
    Delta d;

    make_mesh(&nl, SIDE, SIDE);
    if (nl.nblocks > g.nslots) {
        fprintf(stderr, "блоків більше, ніж слотів\n");
        return 1;
    }
    random_placement(&pl, &nl, &g);

    d.mark    = malloc((size_t)nl.nnets * sizeof(int));
    d.touched = malloc((size_t)nl.nnets * sizeof(int));
    for (int i = 0; i < nl.nnets; i++) d.mark[i] = -1;
    d.stamp = 0;
    d.ntouched = 0;

    long cost = total_hpwl(&nl, &pl, &g);
    printf("блоків %d, сполук %d, слотів %d\n", nl.nblocks, nl.nnets, g.nslots);
    printf("випадковий старт:   HPWL = %ld\n", cost);
    printf("відомий оптимум:    HPWL = %d\n\n", nl.nnets);

    anneal(&nl, &pl, &g, &d, &cost);

    printf("\nпісля відпалу:      HPWL = %ld\n", cost);
    printf("чесний перерахунок: HPWL = %ld  (мусить збігтися)\n",
           total_hpwl(&nl, &pl, &g));

    free(nl.net_off); free(nl.net_pins); free(nl.blk_off); free(nl.blk_nets);
    free(pl.blk_at); free(pl.slot_of); free(d.mark); free(d.touched);
    return 0;
}
