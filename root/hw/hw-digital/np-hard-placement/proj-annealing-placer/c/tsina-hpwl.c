/* HPWL однієї сполуки: обвести всі її виводи рамкою, взяти півпериметр. */
static int net_hpwl(const Netlist *nl, const Placement *pl, const Grid *g, int net)
{
    int lo = nl->net_off[net], hi = nl->net_off[net + 1];
    int s = pl->slot_of[nl->net_pins[lo]];
    int xmin = s % g->W, xmax = xmin;
    int ymin = s / g->W, ymax = ymin;

    for (int p = lo + 1; p < hi; p++) {
        s = pl->slot_of[nl->net_pins[p]];
        int x = s % g->W, y = s / g->W;
        if (x < xmin) xmin = x; else if (x > xmax) xmax = x;
        if (y < ymin) ymin = y; else if (y > ymax) ymax = y;
    }
    return (xmax - xmin) + (ymax - ymin);
}

/* Ціна всієї розкладки. Потрібна рівно двічі: на старті й на перевірці. */
static long total_hpwl(const Netlist *nl, const Placement *pl, const Grid *g)
{
    long sum = 0;
    for (int n = 0; n < nl->nnets; n++)
        sum += net_hpwl(nl, pl, g, n);
    return sum;
}
