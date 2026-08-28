// Читання з каскаду L1 -> L2 -> Singleflight(Origin DB)
HomeState TieredCacheManager::getHomeState(
    const std::string& homeId, 
    std::function<HomeState(const std::string&)> originDBFetch
) {
    std::string cacheKey = "dh:home:" + homeId;

    // 1.Перевірка L1 Process Memory (без мережевого I/O)
    {
        std::shared_lock<std::shared_mutex> lock(l1Mutex_);
        auto it = l1Cache_.find(cacheKey);
        if (it != l1Cache_.end()) {
            return it->second; // L1 HIT
        }
    }

    // 2. Перевірка L2 Redis Cluster (мережевий RTT 1-2 ms)
    auto l2Val = redis_->get(cacheKey);
    if (l2Val.has_value()) {
        populateL1(cacheKey, l2Val.value()); // заповнюємо L1 для наступних викликів
        return l2Val.value(); // L2 HIT
    }

    // 3. L1 & L2 MISS: Викликаємо Singleflight для ізоляції Origin DB
    return singleflight_.doCall(cacheKey, [&]() {
        HomeState freshState = originDBFetch(homeId); // 1 SQL-запит на весь кластер
        redis_->set(cacheKey, freshState, std::chrono::seconds(300));
        populateL1(cacheKey, freshState);
        return freshState;
    });
}
