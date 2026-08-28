static int32_t pick_victim(void)
{
    int32_t s, best = -1;
    double  best_score = -1.0;
    for (s = 0; s < NSEGS; s++) {
        double u, score;
        if (seg[s].is_free) continue;
        if (s == head[0] || s == head[1]) continue;   /* відкриті голови */
        if (seg[s].written == 0) continue;
        u = (double)seg[s].live / (double)SEG_BLOCKS;
        if (policy == GREEDY) {
            score = 1.0 - u;                           /* найпорожніший  */
        } else {
            double age = (double)(now_ - seg[s].sealed);
            score = (1.0 - u) * age / (1.0 + u);       /* вигода/витрати */
        }
        if (score > best_score) { best_score = score; best = s; }
    }
    return best;
}

static int clean_one(void)
{
    int32_t v = pick_victim(), slot;
    if (v < 0) return 0;
    u_sum += (double)seg[v].live / (double)SEG_BLOCKS;   /* статистика   */
    victims++;
    clean_reads += seg[v].written;

    for (slot = 0; slot < seg[v].written; slot++) {
        int32_t ino, off, na;
        if (!block_is_live(v, slot)) continue;          /* перекритий    */
        ino = seg[v].sum[slot].ino;
        off = seg[v].sum[slot].off;
        na  = log_append(ino, off, sep_head);
        if (na < 0) return 0;                           /* немає куди    */
        inode[ino][off] = na;             /* карта показує на нову копію */
        clean_writes++;
    }
    seg[v].is_free = 1;                   /* аж тепер сегмент вільний    */
    seg[v].live    = 0;
    seg[v].written = 0;
    free_segs++;
    return 1;
}

static void ensure_free(void)
{
    while (free_segs < LOW_FREE)
        if (!clean_one()) break;
}
