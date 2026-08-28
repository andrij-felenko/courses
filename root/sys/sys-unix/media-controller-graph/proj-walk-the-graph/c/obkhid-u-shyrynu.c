/* path[] — індекси падів від сенсора до відеовузла; повертає їхню кількість. */
static int find_path(struct graph *g, __u32 from_ent, __u32 to_ent, int *path)
{
    int *prev  = xcalloc(g->npad, sizeof *prev);
    int *queue = xcalloc(g->npad, sizeof *queue);
    int head = 0, tail = 0, found = -1, n = 0;

    for (__u32 i = 0; i < g->npad; i++)
        prev[i] = -2;                                    /* -2 — ще не бачили */

    for (__u32 i = 0; i < g->npad; i++)
        if (g->pad[i].entity_id == from_ent && (g->pad[i].flags & MEDIA_PAD_FL_SOURCE)) {
            prev[i] = -1;                                /* -1 — початок дороги */
            queue[tail++] = (int)i;
        }

    while (head < tail && found < 0) {
        int cur = queue[head++];
        struct media_v2_pad *p = &g->pad[cur];

        if ((p->flags & MEDIA_PAD_FL_SINK) && p->entity_id == to_ent) {
            found = cur;
            break;
        }

        if (p->flags & MEDIA_PAD_FL_SINK) {              /* ребро всередині сутности */
            for (__u32 i = 0; i < g->npad; i++)
                if (g->pad[i].entity_id == p->entity_id && prev[i] == -2 &&
                    (g->pad[i].flags & MEDIA_PAD_FL_SOURCE)) {
                    prev[i] = cur;
                    queue[tail++] = (int)i;
                }
        } else {                                         /* ребро-зв'язок даних */
            for (__u32 k = 0; k < g->nlnk; k++) {
                struct media_v2_pad *s;
                int si;

                if (!is_type(&g->lnk[k], MEDIA_LNK_FL_DATA_LINK) ||
                    g->lnk[k].source_id != p->id)
                    continue;
                if (!(s = pad_by_id(g, g->lnk[k].sink_id)))
                    continue;
                si = (int)(s - g->pad);
                if (prev[si] != -2)
                    continue;
                prev[si] = cur;
                queue[tail++] = si;
            }
        }
    }

    for (int cur = found; cur >= 0; cur = prev[cur])     /* назад по слідах */
        path[n++] = cur;
    for (int i = 0; i < n / 2; i++) {                    /* розвертаємо: від сенсора */
        int t = path[i]; path[i] = path[n - 1 - i]; path[n - 1 - i] = t;
    }
    free(prev); free(queue);
    return n;
}
