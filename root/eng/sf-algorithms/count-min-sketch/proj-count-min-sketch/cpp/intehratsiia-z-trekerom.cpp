class TopKTracker {
public:
    struct Item {
        std::string key;
        uint32_t frequency;
        bool operator>(const Item& other) const noexcept {
            return frequency > other.frequency;
        }
    };

    TopKTracker(size_t k, double epsilon, double delta)
        : k_(k), sketch_(epsilon, delta) {}

    void add(std::string_view key, uint32_t count = 1) {
        sketch_.update_conservative(key, count);
        uint32_t est = sketch_.estimate(key);
        
        auto it = map_.find(std::string(key));
        if (it != map_.end()) {
            it->second = est;
            rebuild_heap();
        } else if (heap_.size() < k_) {
            map_[std::string(key)] = est;
            heap_.push_back({std::string(key), est});
            std::push_heap(heap_.begin(), heap_.end(), std::greater<Item>{});
        } else if (est > heap_.front().frequency) {
            map_.erase(heap_.front().key);
            map_[std::string(key)] = est;
            std::pop_heap(heap_.begin(), heap_.end(), std::greater<Item>{});
            heap_.back() = {std::string(key), est};
            std::push_heap(heap_.begin(), heap_.end(), std::greater<Item>{});
        }
    }

    [[nodiscard]] std::vector<Item> top_k() const {
        auto result = heap_;
        std::sort(result.begin(), result.end(), [](const Item& a, const Item& b) {
            return a.frequency > b.frequency;
        });
        return result;
    }

private:
    void rebuild_heap() {
        heap_.clear();
        for (const auto& [k, v] : map_) {
            heap_.push_back({k, v});
        }
        std::make_heap(heap_.begin(), heap_.end(), std::greater<Item>{});
    }

    size_t k_;
    CountMinSketch sketch_;
    std::vector<Item> heap_;
    std::unordered_map<std::string, uint32_t> map_;
};
