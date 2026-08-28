public:
    [[nodiscard]] std::optional<Value> find(const Key &key) const {
        if (size_ == 0) return std::nullopt;

        // 1. Перевірка слота в першій таблиці
        const size_t i1 = index1(key);
        if (t1_[i1].occupied && t1_[i1].key == key) {
            return t1_[i1].value;
        }

        // 2. Перевірка слота в другій таблиці
        const size_t i2 = index2(key);
        if (t2_[i2].occupied && t2_[i2].key == key) {
            return t2_[i2].value;
        }

        // 3. Перевірка схованки
        for (const auto &slot : stash_) {
            if (slot.occupied && slot.key == key) {
                return slot.value;
            }
        }

        return std::nullopt;
    }
