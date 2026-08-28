#include <iostream>
#include <string>
#include <string_view>
#include <unordered_map>
#include <shared_mutex>
#include <mutex>
#include <optional>
#include <chrono>
#include <cstdint>
#include <thread>

enum class CacheGetStatus {
    Hit,
    MissLeaseGranted,
    MissLeaseBusy
};

enum class CacheSetStatus {
    Success,
    StaleTokenRejected
};

struct GetResult {
    CacheGetStatus status;
    std::string value;
    uint64_t token{0};
};

class LeaseCache {
public:
    explicit LeaseCache(std::chrono::seconds lease_duration = std::chrono::seconds(5))
        : lease_ttl_(lease_duration) {}

    GetResult get(std::string_view key) {
        std::unique_lock<std::shared_mutex> lock(mutex_);
        auto& entry = table_[std::string(key)];
        auto now = std::chrono::steady_clock::now();

        if (entry.is_valid) {
            return {CacheGetStatus::Hit, entry.value, 0};
        }

        if (entry.active_lease_token != 0 && now < entry.lease_expiry) {
            return {CacheGetStatus::MissLeaseBusy, "", 0};
        }

        entry.active_lease_token = ++global_token_counter_;
        entry.lease_expiry = now + lease_ttl_;
        return {CacheGetStatus::MissLeaseGranted, "", entry.active_lease_token};
    }

    CacheSetStatus set(std::string_view key, std::string_view value, uint64_t token) {
        std::unique_lock<std::shared_mutex> lock(mutex_);
        auto it = table_.find(std::string(key));
        if (it == table_.end() || it->second.active_lease_token != token) {
            return CacheSetStatus::StaleTokenRejected;
        }

        auto& entry = it->second;
        entry.value = value;
        entry.is_valid = true;
        entry.active_lease_token = 0;
        ++entry.generation;
        return CacheSetStatus::Success;
    }

    void invalidate(std::string_view key) {
        std::unique_lock<std::shared_mutex> lock(mutex_);
        auto it = table_.find(std::string(key));
        if (it != table_.end()) {
            it->second.is_valid = false;
            ++it->second.generation;
            it->second.active_lease_token = 0;
        }
    }

private:
    struct Entry {
        std::string value;
        bool is_valid{false};
        uint64_t generation{1};
        uint64_t active_lease_token{0};
        std::chrono::steady_clock::time_point lease_expiry;
    };

    mutable std::shared_mutex mutex_;
    std::unordered_map<std::string, Entry> table_;
    uint64_t global_token_counter_{1000};
    std::chrono::seconds lease_ttl_;
};
