[[nodiscard]] std::optional<size_t> find_best_free_block() const noexcept {
    std::optional<size_t> best_block;
    uint32_t min_erase = UINT32_MAX;

    for (size_t b = 0; b < blocks_.size(); ++b) {
        if (b != active_block_id_ && blocks_[b].is_clean()) {
            if (blocks_[b].erase_count < min_erase) {
                min_erase = blocks_[b].erase_count;
                best_block = b;
            }
        }
    }
    return best_block;
}
