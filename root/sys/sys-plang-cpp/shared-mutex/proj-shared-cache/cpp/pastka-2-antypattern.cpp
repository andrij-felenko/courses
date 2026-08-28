// ❌ КРАХ ПРОГРАМИ — НЕЗДОЛАНИЙ ГЛУХИЙ КУТ (DEADLOCK)!
Value get_or_load(const Key& key) {
    std::shared_lock<std::shared_mutex> lock(mutex_);
    auto it = cache_.find(key);
    if (it != cache_.end()) {
        return it->second.value;
    }

    // Спроба "підвищити" режим блокування без розблокування читання
    std::unique_lock<std::shared_mutex> writer_lock(mutex_); // 💥 DEADLOCK!
    Value val = load_from_db(key);
    cache_[key] = val;
    return val;
}
