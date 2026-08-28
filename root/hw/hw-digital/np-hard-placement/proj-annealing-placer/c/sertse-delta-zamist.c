/* Додати до списку зачеплених усі сполуки блока — БЕЗ ПОВТОРІВ.
   Мітка-номер-ходу дає перевірку «вже брали?» за O(1) і не потребує
   чистити масив після кожного ходу. */
static void collect_nets(const Netlist *nl, Delta *d, int blk)
{
    if (blk < 0) return;                    /* порожній слот — сполук нема */
    for (int i = nl->blk_off[blk]; i < nl->blk_off[blk + 1]; i++) {
        int net = nl->blk_nets[i];
        if (d->mark[net] != d->stamp) {
            d->mark[net] = d->stamp;
            d->touched[d->ntouched++] = net;
        }
    }
}

/* Δ ціни від обміну слотів s1 ↔ s2.
   УВАГА: після виклику обмін ЗАСТОСОВАНИЙ. Хто не прийняв — хай відкотить. */
static int swap_delta(const Netlist *nl, Placement *pl, const Grid *g,
                      Delta *d, int s1, int s2)
{
    d->stamp++;
    d->ntouched = 0;
    collect_nets(nl, d, pl->blk_at[s1]);
    collect_nets(nl, d, pl->blk_at[s2]);

    int before = 0;
    for (int i = 0; i < d->ntouched; i++)
        before += net_hpwl(nl, pl, g, d->touched[i]);

    apply_swap(pl, s1, s2);

    /* Множина зачеплених сполук ТА САМА: обмін міняє КООРДИНАТИ блоків,
       а не те, до яких сполук вони належать. Тому збираємо раз, а міряємо двічі. */
    int after = 0;
    for (int i = 0; i < d->ntouched; i++)
        after += net_hpwl(nl, pl, g, d->touched[i]);

    return after - before;
}
