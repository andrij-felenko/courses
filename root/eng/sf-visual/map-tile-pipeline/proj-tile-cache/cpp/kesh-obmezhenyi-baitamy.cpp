struct Raster {
    int32_t width = 0, height = 0, bytesPerPixel = 4;
    std::vector<uint8_t> pixels;
    // Скільки пам'яті РЕАЛЬНО зайнято, а не скільки мало б бути.
    size_t footprint() const noexcept { return pixels.capacity(); }
};

using RasterPtr = std::shared_ptr<const Raster>;

class TileCache {
public:
    explicit TileCache(size_t budgetBytes) : budget_(budgetBytes) {}

    // Влучання віддає ВОЛОДІННЯ. Покажчик у нутрощі кеша віддавати не можна:
    // до наступного кадру запис переїде на інше місце або зникне зовсім.
    RasterPtr find(const TileId& id) const {
        const auto it = index_.find(id);
        return it == index_.end() ? RasterPtr{} : entries_[it->second].raster;
    }

    void insert(const TileId& id, RasterPtr raster) {
        const size_t bytes = raster->footprint() + kEntryOverhead;
        const auto [it, fresh] = index_.emplace(id, entries_.size());
        if (!fresh) {
            Entry& old = entries_[it->second];
            bytes_ -= old.bytes;            // ← спершу відняти старе, і лише потім додати
            old.raster = std::move(raster);
            old.bytes  = bytes;
            bytes_ += bytes;
            return;
        }
        entries_.push_back(Entry{ id, std::move(raster), bytes });
        bytes_ += bytes;
    }

    void erase(const TileId& id) {
        const auto it = index_.find(id);
        if (it == index_.end()) return;
        const size_t i = it->second;
        bytes_ -= entries_[i].bytes;
        index_.erase(it);                   // ітератор далі не потрібен — знімаємо його першим
        const size_t last = entries_.size() - 1;
        if (i != last) {                    // дірку в масиві затикаємо останнім елементом
            entries_[i] = std::move(entries_[last]);
            index_.find(entries_[i].id)->second = i;   // переставленому — новий індекс
        }
        entries_.pop_back();
    }

    size_t bytes() const noexcept { return bytes_; }

    // Один прохід до НИЖНЬОЇ межі. Кличуть у потоці малювання й лише коли перебір.
    void trim(const Viewport& vp) {
        if (bytes_ <= budget_) return;
        const size_t target = size_t(double(budget_) * kLowWater);

        order_.resize(entries_.size());
        value_.resize(entries_.size());
        for (size_t i = 0; i < entries_.size(); ++i) {
            order_[i] = uint32_t(i);
            value_[i] = cacheValue(entries_[i].id, vp);
        }
        std::sort(order_.begin(), order_.end(),
                  [this](uint32_t a, uint32_t b) { return value_[a] < value_[b]; });

        // Спершу зібрати АДРЕСИ, і тільки потім видаляти: erase() переставляє
        // елементи вектора, і збережені індекси після першого ж видалення брешуть.
        victims_.clear();
        size_t freed = 0;
        for (const uint32_t i : order_) {
            if (bytes_ - freed <= target) break;
            freed += entries_[i].bytes;
            victims_.push_back(entries_[i].id);
        }
        for (const TileId& id : victims_) erase(id);
    }

private:
    struct Entry { TileId id; RasterPtr raster; size_t bytes; };

    // Entry + вузол хеш-таблиці + блок керування shared_ptr + заголовок алокатора.
    static constexpr size_t kEntryOverhead = 128;
    static constexpr double kLowWater      = 0.85;

    std::vector<Entry> entries_;
    std::unordered_map<TileId, size_t, TileHash> index_;
    size_t bytes_ = 0;
    size_t budget_;

    std::vector<uint32_t> order_;    // робочі буфери trim — щоб він не алокував
    std::vector<double>   value_;
    std::vector<TileId>   victims_;
};
