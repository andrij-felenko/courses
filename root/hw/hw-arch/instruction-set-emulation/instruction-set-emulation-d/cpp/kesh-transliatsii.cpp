constexpr size_t TBCacheSize = 65536;

inline size_t tb_hash(uint32_t pc) noexcept {
    return (pc ^ (pc >> 6)) & (TBCacheSize - 1);
}

class TranslationCache {
public:
    TranslationBlock* find(uint32_t guest_pc) noexcept {
        size_t idx = tb_hash(guest_pc);
        TranslationBlock* tb = table_[idx];
        if (tb && tb->guest_pc == guest_pc) {
            return tb;
        }
        return nullptr;
    }

    void insert(TranslationBlock* tb) noexcept {
        table_[tb_hash(tb->guest_pc)] = tb;
    }

private:
    std::array<TranslationBlock*, TBCacheSize> table_{};
};
