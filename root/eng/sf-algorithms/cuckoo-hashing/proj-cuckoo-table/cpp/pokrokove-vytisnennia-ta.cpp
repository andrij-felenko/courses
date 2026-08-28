public:
    bool insert(const Key &key, const Value &value) {
        // Оновлення значення, якщо ключ уже присутній
        const size_t i1 = index1(key);
        if (t1_[i1].occupied && t1_[i1].key == key) {
            t1_[i1].value = value;
            return true;
        }
        const size_t i2 = index2(key);
        if (t2_[i2].occupied && t2_[i2].key == key) {
            t2_[i2].value = value;
            return true;
        }
        for (auto &slot : stash_) {
            if (slot.occupied && slot.key == key) {
                slot.value = value;
                return true;
            }
        }

        Entry current{key, value, true};
        return insert_entry(current);
    }

private:
    bool insert_entry(Entry current) {
        const size_t max_steps = capacity_ * MaxDisplacementsFactor;

        for (size_t step = 0; step < max_steps; ++step) {
            // Спроба вставки в T1
            const size_t p1 = index1(current.key);
            if (!t1_[p1].occupied) {
                t1_[p1] = current;
                ++size_;
                return true;
            }
            std::swap(t1_[p1], current);

            // Спроба вставки в T2
            const size_t p2 = index2(current.key);
            if (!t2_[p2].occupied) {
                t2_[p2] = current;
                ++size_;
                return true;
            }
            std::swap(t2_[p2], current);
        }

        // Розміщення в схованці при перевищенні ліміту витіснень
        for (auto &slot : stash_) {
            if (!slot.occupied) {
                slot = current;
                ++size_;
                return true;
            }
        }

        // Перехешування та подвоєння місткості
        rehash(capacity_ * 2);
        return insert_entry(current);
    }

    void rehash(size_t new_capacity) {
        std::vector<Entry> old_t1 = std::move(t1_);
        std::vector<Entry> old_t2 = std::move(t2_);
        std::array<Entry, StashCapacity> old_stash = stash_;

        capacity_ = new_capacity;
        size_ = 0;
        seed1_ += 0x9E3779B9ULL;
        seed2_ += 0xC6A4A793ULL;

        t1_.assign(capacity_, Entry{});
        t2_.assign(capacity_, Entry{});
        stash_.fill(Entry{});

        for (const auto &entry : old_t1) {
            if (entry.occupied) insert_entry(entry);
        }
        for (const auto &entry : old_t2) {
            if (entry.occupied) insert_entry(entry);
        }
        for (const auto &entry : old_stash) {
            if (entry.occupied) insert_entry(entry);
        }
    }
