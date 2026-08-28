#include <iostream>
#include <string>
#include <unordered_map>
#include <shared_mutex>
#include <chrono>
#include <memory>
#include <atomic>

struct RegionTarget {
    std::string primary_region;
    std::string failover_region;
    uint64_t fencing_epoch;
    bool is_read_only;
};

class GlobalDirectoryClient {
public:
    virtual ~GlobalDirectoryClient() = default;
    virtual std::shared_ptr<RegionTarget> lookup_home_region(const std::string& home_id) = 0;
};

class GeoRouter {
private:
    struct CacheEntry {
        std::shared_ptr<RegionTarget> target;
        std::chrono::steady_clock::time_point created_at;
    };

    std::shared_ptr<GlobalDirectoryClient> dir_client_;
    std::unordered_map<std::string, CacheEntry> cache_;
    mutable std::shared_mutex cache_mutex_;
    std::chrono::milliseconds ttl_;
    std::atomic<uint64_t> hits_{0};
    std::atomic<uint64_t> misses_{0};

    std::string validate_and_route(const std::shared_ptr<RegionTarget>& target, uint64_t client_epoch) const {
        if (client_epoch < target->fencing_epoch) {
            throw std::runtime_error("FENCING_EPOCH_STALE: Target region is isolated");
        }
        return target->primary_region;
    }

public:
    GeoRouter(std::shared_ptr<GlobalDirectoryClient> client, std::chrono::milliseconds ttl)
        : dir_client_(std::move(client)), ttl_(ttl) {}

    std::string resolve_region(const std::string& home_id, uint64_t client_epoch) {
        {
            std::shared_lock<std::shared_mutex> lock(cache_mutex_);
            auto it = cache_.find(home_id);
            if (it != cache_.end()) {
                auto age = std::chrono::steady_clock::now() - it->second.created_at;
                if (age < ttl_) {
                    hits_.fetch_add(1, std::memory_order_relaxed);
                    return validate_and_route(it->second.target, client_epoch);
                }
            }
        }

        misses_.fetch_add(1, std::memory_order_relaxed);

        auto target = dir_client_->lookup_home_region(home_id);
        if (!target) {
            throw std::runtime_error("Home ID not found in Global Directory");
        }

        {
            std::unique_lock<std::shared_mutex> lock(cache_mutex_);
            cache_[home_id] = CacheEntry{target, std::chrono::steady_clock::now()};
        }

        return validate_and_route(target, client_epoch);
    }
};
