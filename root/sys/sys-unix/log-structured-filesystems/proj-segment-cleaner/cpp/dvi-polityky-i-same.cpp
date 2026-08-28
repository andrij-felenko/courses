static std::int32_t pick_victim() {
    std::int32_t best_seg = -1;
    double best_score = -1.0;
    for (std::size_t s = 0; s < NSEGS; ++s) {
        if (state.seg[s].is_free) continue;
        if (static_cast<std::int32_t>(s) == state.head[0] ||
            static_cast<std::int32_t>(s) == state.head[1]) continue;
        if (state.seg[s].written == 0) continue;

        double u = static_cast<double>(state.seg[s].live) / static_cast<double>(SEG_BLOCKS);
        double score = 0.0;
        if (state.policy == Policy::Greedy) {
            score = 1.0 - u;
        } else {
            double age = static_cast<double>(state.now_ - state.seg[s].sealed);
            score = (1.0 - u) * age / (1.0 + u);
        }
        if (score > best_score) {
            best_score = score;
            best_seg = static_cast<std::int32_t>(s);
        }
    }
    return best_seg;
}

static bool clean_one() {
    std::int32_t v = pick_victim();
    if (v < 0) return false;

    state.u_sum += static_cast<double>(state.seg[v].live) / static_cast<double>(SEG_BLOCKS);
    state.victims++;
    state.clean_reads += state.seg[v].written;

    for (std::int32_t slot = 0; slot < state.seg[v].written; ++slot) {
        if (!block_is_live(v, slot)) continue;
        std::int32_t ino = state.seg[v].sum[slot].ino;
        std::int32_t off = state.seg[v].sum[slot].off;
        std::int32_t na  = log_append(ino, off, state.sep_head);
        if (na < 0) return false;
        state.inode[ino][off] = na;
        state.clean_writes++;
    }
    state.seg[v].is_free = true;
    state.seg[v].live    = 0;
    state.seg[v].written = 0;
    state.free_segs++;
    return true;
}

static void ensure_free() {
    while (state.free_segs < LOW_FREE) {
        if (!clean_one()) break;
    }
}
