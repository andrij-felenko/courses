// CLOCK: кільце слотів + один БАЙТ прапорця на слот (не біт — див. нижче).
template <class K, class V>
class ClockCache {
    struct Slot { K key; V val; };

    std::vector<Slot> slots_;
    std::vector<uint8_t> ref_;                // прапорці звернення
    std::unordered_map<K, uint32_t> index_;
    uint32_t hand_ = 0, cap_;
    uint64_t hits_ = 0, misses_ = 0, evictions_ = 0, steps_ = 0;

public:
    explicit ClockCache(uint32_t cap) : cap_(cap) {
        slots_.reserve(cap_);
        ref_.reserve(cap_);
        index_.reserve(cap_ * 2);
    }

    std::optional<V> get(const K& key) {
        auto it = index_.find(key);
        if (it == index_.end()) { ++misses_; return std::nullopt; }
        ++hits_;
        ref_[it->second] = 1;                 // УВЕСЬ облік свіжості — цей рядок
        return slots_[it->second].val;
    }

    void put(const K& key, V val) {
        if (auto it = index_.find(key); it != index_.end()) {
            slots_[it->second].val = std::move(val);
            ref_[it->second] = 1;
            return;
        }
        uint32_t i;
        if (slots_.size() < cap_) {
            i = static_cast<uint32_t>(slots_.size());
            slots_.push_back(Slot{key, std::move(val)});
            ref_.push_back(1);
        } else {
            i = evict();                      // слот i звільнено й вилучено з індексу
            slots_[i] = Slot{key, std::move(val)};
            ref_[i] = 1;
        }
        index_.emplace(key, i);
    }

    double steps_per_eviction() const {
        return evictions_ ? static_cast<double>(steps_) / evictions_ : 0.0;
    }

private:
    uint32_t evict() {
        for (;;) {
            uint32_t i = hand_;
            hand_ = (hand_ + 1 == cap_) ? 0 : hand_ + 1;
            ++steps_;
            if (ref_[i] == 0) {               // жертва знайдена
                index_.erase(slots_[i].key);  // ключ ще на місці — слот не чіпали
                ++evictions_;
                return i;
            }
            ref_[i] = 0;                      // другий шанс
        }
    }
};
