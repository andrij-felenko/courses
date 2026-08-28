class Store {
public:
    explicit Store(size_t capacity_bytes) : cap_(capacity_bytes) {}

    // повертає ЗНІМОК: поки виклик тримає shared_ptr, витіснення не звільнить тіла
    std::shared_ptr<const Entry> lookup(const std::string& method, const std::string& url,
                                        const Fields& request) {
        std::lock_guard<std::mutex> g(mu_);
        const auto it = index_.find(primary(method, url));
        if (it == index_.end()) return nullptr;
        for (auto node : it->second) {
            if (variant_matches(**node, request)) {
                lru_.splice(lru_.begin(), lru_, node);   // ітератори лишаються чинними
                return *node;
            }
        }
        return nullptr;
    }

    void put(std::shared_ptr<Entry> e) {
        std::lock_guard<std::mutex> g(mu_);
        auto& bucket = index_[primary(e->method, e->url)];
        for (auto node : bucket)
            if ((*node)->selecting == e->selecting) {     // той самий варіант — заміна
                bytes_ -= footprint(**node);
                *node   = std::move(e);
                bytes_ += footprint(**node);
                lru_.splice(lru_.begin(), lru_, node);
                evict_locked();
                return;
            }
        lru_.push_front(std::move(e));
        bucket.push_back(lru_.begin());
        bytes_ += footprint(*lru_.front());
        evict_locked();
    }

private:
    using Node = std::list<std::shared_ptr<Entry>>::iterator;

    void evict_locked() {
        while (bytes_ > cap_ && !lru_.empty()) {
            const Node victim = std::prev(lru_.end());
            const std::string key = primary((*victim)->method, (*victim)->url);
            auto& bucket = index_[key];
            bucket.erase(std::find(bucket.begin(), bucket.end(), victim));
            bytes_ -= footprint(**victim);
            const bool drained = bucket.empty();
            lru_.erase(victim);        // якщо хтось читає запис, його shared_ptr тримає тіло
            if (drained) index_.erase(key);
        }
    }

    static size_t footprint(const Entry& e) {
        // тіло, заголовки й сам ключ; без останніх двох злива дрібних 404
        // з довгими адресами переповнить пам'ять при цілком «здоровому» bytes_
        return e.body.size() + e.headers.bytes() + e.url.size() + 256;
    }
    static std::string primary(const std::string& m, const std::string& u) { return m + " " + u; }

    std::mutex mu_;
    std::list<std::shared_ptr<Entry>> lru_;                 // спереду — щойно вжите
    std::unordered_map<std::string, std::vector<Node>> index_;
    size_t bytes_ = 0, cap_;
};
