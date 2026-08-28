static std::int32_t alloc_segment(bool is_cleaner) {
    if (!is_cleaner && state.free_segs <= RESERVE) return -1;
    for (std::size_t s = 0; s < NSEGS; ++s) {
        if (!state.seg[s].is_free) continue;
        state.seg[s].is_free = false;
        state.seg[s].written = 0;
        state.seg[s].live    = 0;
        for (auto& entry : state.seg[s].sum) entry.ino = -1;
        state.free_segs--;
        return static_cast<std::int32_t>(s);
    }
    return -1;
}

static std::int32_t log_append(std::int32_t ino, std::int32_t off, bool is_cleaner) {
    std::size_t h_idx = is_cleaner ? 1 : 0;
    std::int32_t s = state.head[h_idx];
    if (s < 0 || state.seg[s].written == static_cast<std::int32_t>(SEG_BLOCKS)) {
        s = alloc_segment(is_cleaner);
        if (s < 0) return -1;
        state.head[h_idx] = s;
    }
    std::int32_t slot = state.seg[s].written++;
    state.seg[s].sum[slot] = SummaryEntry{ino, off};
    state.seg[s].live++;
    state.seg[s].sealed = ++state.now_;
    return s * static_cast<std::int32_t>(SEG_BLOCKS) + slot;
}

static bool file_write(std::int32_t ino, std::int32_t off) {
    std::int32_t old_addr = state.inode[ino][off];
    std::int32_t new_addr = log_append(ino, off, false);
    if (new_addr < 0) {
        state.stalls++;
        return false;
    }
    state.inode[ino][off] = new_addr;
    if (old_addr >= 0) {
        state.seg[old_addr / SEG_BLOCKS].live--;
    }
    state.user_writes++;
    return true;
}
