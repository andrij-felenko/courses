#include <chrono>
#include <iostream>
#include <optional>
#include <shared_mutex>
#include <string>
#include <thread>
#include <unordered_map>

class ThreadSafeRegistry {
public:
    // Операція читання: багато потоків читають одночасно
    std::optional<std::string> get(const std::string& key) const {
        std::shared_lock<std::shared_mutex> lock(mutex_);
        auto it = map_.find(key);
        if (it != map_.end()) {
            return it->second;
        }
        return std::nullopt;
    }

    // Операція запису: монопольний доступ одного потоку
    void set(const std::string& key, const std::string& value) {
        std::unique_lock<std::shared_mutex> lock(mutex_);
        map_[key] = value;
    }

    // Операція читання з обмеженням за часом очікування
    std::optional<std::string> get_timed(const std::string& key, std::chrono::milliseconds timeout) const {
        std::shared_lock<std::shared_timed_mutex> lock(timed_mutex_, timeout);
        if (!lock.owns_lock()) {
            return std::nullopt; // Таймаут очікування замка
        }
        auto it = timed_map_.find(key);
        if (it != timed_map_.end()) {
            return it->second;
        }
        return std::nullopt;
    }

private:
    mutable std::shared_mutex                   mutex_;
    std::unordered_map<std::string, std::string> map_;

    mutable std::shared_timed_mutex             timed_mutex_;
    std::unordered_map<std::string, std::string> timed_map_;
};
