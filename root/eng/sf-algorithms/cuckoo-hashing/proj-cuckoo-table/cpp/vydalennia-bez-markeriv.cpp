public:
    bool erase(const Key &key) {
        if (size_ == 0) return false;

        const size_t i1 = index1(key);
        if (t1_[i1].occupied && t1_[i1].key == key) {
            t1_[i1].occupied = false;
            --size_;
            return true;
        }

        const size_t i2 = index2(key);
        if (t2_[i2].occupied && t2_[i2].key == key) {
            t2_[i2].occupied = false;
            --size_;
            return true;
        }

        for (auto &slot : stash_) {
            if (slot.occupied && slot.key == key) {
                slot.occupied = false;
                --size_;
                return true;
            }
        }

        return false;
    }
