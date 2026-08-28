static int32_t alloc_segment(int cleaner)
{
    int32_t s, i;
    if (!cleaner && free_segs <= RESERVE) return -1;   /* резерв прибирача */
    for (s = 0; s < NSEGS; s++) {
        if (!seg[s].is_free) continue;
        seg[s].is_free = 0;
        seg[s].written = 0;
        seg[s].live    = 0;
        for (i = 0; i < SEG_BLOCKS; i++) seg[s].sum[i].ino = -1;
        free_segs--;
        return s;
    }
    return -1;
}

static int32_t log_append(int32_t ino, int32_t off, int cleaner)
{
    int32_t s = head[cleaner], slot;
    if (s < 0 || seg[s].written == SEG_BLOCKS) {   /* голова заповнилась */
        s = alloc_segment(cleaner);
        if (s < 0) return -1;                      /* класти нікуди      */
        head[cleaner] = s;
    }
    slot = seg[s].written++;
    seg[s].sum[slot].ino = ino;                    /* підсумковий блок   */
    seg[s].sum[slot].off = off;
    seg[s].live++;
    seg[s].sealed = ++now_;
    return s * SEG_BLOCKS + slot;
}

static int file_write(int32_t ino, int32_t off)
{
    int32_t old = inode[ino][off];
    int32_t na  = log_append(ino, off, 0);
    if (na < 0) { stalls++; return 0; }
    inode[ino][off] = na;
    if (old >= 0) seg[old / SEG_BLOCKS].live--;    /* стара версія вмерла */
    user_writes++;
    return 1;
}
