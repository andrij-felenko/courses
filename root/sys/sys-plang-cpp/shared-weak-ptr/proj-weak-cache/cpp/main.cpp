class TextureCache : public std::enable_shared_from_this<TextureCache> {
public:
    static std::shared_ptr<TextureCache> create() {
        return std::shared_ptr<TextureCache>(new TextureCache);
    }

    std::shared_ptr<Texture> get(const std::string& key) {
        {                                    // 1. швидкий шлях під замком
            std::lock_guard lock(mutex_);
            auto it = entries_.find(key);
            if (it != entries_.end())
                if (auto alive = it->second.lock())
                    return alive;
        }

        // 2. важке завантаження — БЕЗ замка, кеш обслуговує інших
        std::shared_ptr<Texture> fresh(
            new Texture(key),
            [weak_self = weak_from_this(), key](Texture* raw) {
                delete raw;                             // спершу смерть об'єкта
                if (auto cache = weak_self.lock())
                    cache->drop(key);                   // потім прибирання запису
            });

        // 3. публікація: поки ми вантажили, хтось міг устигнути перший
        std::lock_guard lock(mutex_);
        auto& slot = entries_[key];
        if (auto winner = slot.lock())
            return winner;                   // наш fresh знищиться на виході
        slot = fresh;
        return fresh;
    }

private:
    TextureCache() = default;

    void drop(const std::string& key) {
        std::lock_guard lock(mutex_);
        auto it = entries_.find(key);
        if (it != entries_.end() && it->second.expired())
            entries_.erase(it);              // живого наступника не чіпаємо
    }

    std::mutex mutex_;
    std::unordered_map<std::string, std::weak_ptr<Texture>> entries_;
};
