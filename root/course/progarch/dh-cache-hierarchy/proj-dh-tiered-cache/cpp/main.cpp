#include <iostream>
#include <string>
#include <unordered_map>
#include <shared_mutex>
#include <mutex>
#include <memory>
#include <optional>
#include <future>
#include <chrono>
#include <functional>
#include <vector>
#include <stdexcept>

// DTO стану пристрою та дому
struct DeviceState {
    std::string id;
    std::string type;
    std::string status;
    double value;
};

struct HomeState {
    std::string homeId;
    std::vector<DeviceState> devices;
    uint64_t version{0}; // Монотонна версія для запобігання race conditions
};

// Симулятор L2 Redis Клієнта та мережевого транспортного шару
class RedisClientMock {
public:
    std::optional<HomeState> get(const std::string& key) {
        std::shared_lock<std::shared_mutex> lock(mutex_);
        auto it = store_.find(key);
        if (it != store_.end()) {
            return it->second;
        }
        return std::nullopt;
    }

    void set(const std::string& key, const HomeState& state, std::chrono::seconds ttl) {
        std::unique_lock<std::shared_mutex> lock(mutex_);
        auto it = store_.find(key);
        if (it == store_.end() || state.version >= it->second.version) {
            store_[key] = state;
        }
    }

    void publishInvalidation(const std::string& channel, const std::string& key, uint64_t version) {
        std::cout << "[L2 Redis Pub/Sub] Evict broadcast on channel '" << channel 
                  << "' for key: " << key << " (v" << version << ")" << std::endl;
    }

private:
    std::unordered_map<std::string, HomeState> store_;
    std::shared_mutex mutex_;
};

// Схлопувач запитів (Singleflight / Request Coalescing)
// Гарантує, що при N паралельних промахах кешу виконується РІВНО ОДИН запит до Origin DB
class SingleflightGroup {
public:
    using Fetcher = std::function<HomeState()>;

    HomeState doCall(const std::string& key, Fetcher fetcher) {
        std::shared_ptr<Call> callPtr;
        bool isLeader = false;

        {
            std::lock_guard<std::mutex> lock(mutex_);
            auto it = calls_.find(key);
            if (it != calls_.end()) {
                // Запит вже виконується іншим потоком — підключаємося до його future
                callPtr = it->second;
            } else {
                // Поточний потік є першим (лідером) — створюємо новий запит
                callPtr = std::make_shared<Call>();
                callPtr->futureResult = callPtr->promiseResult.get_future().share();
                calls_[key] = callPtr;
                isLeader = true;
            }
        }

        if (!isLeader) {
            // Ведені потоки чекають завершення лідера без генерації повторних SQL-запитів
            return callPtr->futureResult.get();
        }

        // Лідери виконують реальний фетч із бази даних
        try {
            HomeState res = fetcher();
            callPtr->promiseResult.set_value(res);

            std::lock_guard<std::mutex> lock(mutex_);
            calls_.erase(key);
            return res;
        } catch (...) {
            callPtr->promiseResult.set_exception(std::current_exception());
            std::lock_guard<std::mutex> lock(mutex_);
            calls_.erase(key);
            throw;
        }
    }

private:
    struct Call {
        std::promise<HomeState> promiseResult;
        std::shared_future<HomeState> futureResult;
    };

    std::mutex mutex_;
    std::unordered_map<std::string, std::shared_ptr<Call>> calls_;
};

// Потокобезпечний трирівневий менеджер кешу DH
class TieredCacheManager {
public:
    explicit TieredCacheManager(std::shared_ptr<RedisClientMock> redis)
        : redis_(std::move(redis)) {}

    // ── Read Path ─────────────────────────────────────────────────────────────
    HomeState getHomeState(const std::string& homeId, std::function<HomeState(const std::string&)> originDBFetch) {
        std::string cacheKey = "dh:home:" + homeId;

        // Ярус 1: Перевірка L1 Process Memory (без мережевих затримок)
        {
            std::shared_lock<std::shared_mutex> lock(l1Mutex_);
            auto it = l1Cache_.find(cacheKey);
            if (it != l1Cache_.end()) {
                std::cout << "[L1 HIT] Home " << homeId << " (v" << it->second.version << ") from RAM." << std::endl;
                return it->second;
            }
        }

        // Ярус 2: Перевірка L2 Redis Cluster (мережевий RTT 1-2 ms)
        auto l2Opt = redis_->get(cacheKey);
        if (l2Opt.has_value()) {
            std::cout << "[L2 HIT] Home " << homeId << " (v" << l2Opt->version << ") from Redis." << std::endl;
            populateL1(cacheKey, l2Opt.value());
            return l2Opt.value();
        }

        // Ярус 3: L1/L2 MISS — Виклик Singleflight для ізоляції Origin DB
        std::cout << "[L1/L2 MISS] Singleflight coalescing for home: " << homeId << std::endl;
        return singleflight_.doCall(cacheKey, [&]() {
            HomeState stateFromDB = originDBFetch(homeId);

            // Заповнюємо L2 та L1 для наступних викликів
            redis_->set(cacheKey, stateFromDB, std::chrono::seconds(300));
            populateL1(cacheKey, stateFromDB);

            return stateFromDB;
        });
    }

    // ── Write Path & Eviction ──────────────────────────────────────────────────
    void updateHomeState(const HomeState& newState, std::function<void(const HomeState&)> originDBSave) {
        std::string cacheKey = "dh:home:" + newState.homeId;

        // 1. Атомарний запис у база даних (сховище правди)
        originDBSave(newState);

        // 2. Оновлення L2 Redis
        redis_->set(cacheKey, newState, std::chrono::seconds(300));

        // 3. Інвалідація локального L1
        invalidateL1(cacheKey, newState.version);

        // 4. Публікація евенту інвалідації для сусідніх API-вузлів
        redis_->publishInvalidation("dh:invalidation", cacheKey, newState.version);

        // 5. Виклик L3 Edge CDN Purge API за Surrogate Key
        purgeEdgeCDN(newState.homeId);
    }

    // Обробник Pub/Sub повідомлення про інвалідацію від іншого вузла
    void invalidateL1(const std::string& cacheKey, uint64_t newVersion) {
        std::unique_lock<std::shared_mutex> lock(l1Mutex_);
        auto it = l1Cache_.find(cacheKey);
        if (it != l1Cache_.end()) {
            if (newVersion >= it->second.version) {
                l1Cache_.erase(it);
                std::cout << "[L1 EVICT] Removed key: " << cacheKey << " (v" << newVersion << ")" << std::endl;
            }
        }
    }

private:
    void populateL1(const std::string& key, const HomeState& state) {
        std::unique_lock<std::shared_mutex> lock(l1Mutex_);
        auto it = l1Cache_.find(key);
        if (it == l1Cache_.end() || state.version >= it->second.version) {
            l1Cache_[key] = state;
        }
    }

    void purgeEdgeCDN(const std::string& homeId) {
        std::cout << "[L3 CDN PURGE] Triggered Soft Purge for Surrogate-Key: home-" << homeId << std::endl;
    }

    std::shared_mutex l1Mutex_;
    std::unordered_map<std::string, HomeState> l1Cache_;
    std::shared_ptr<RedisClientMock> redis_;
    SingleflightGroup singleflight_;
};
