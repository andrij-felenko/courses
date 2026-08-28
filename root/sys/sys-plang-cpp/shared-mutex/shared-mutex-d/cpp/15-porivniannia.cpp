#include <iostream>
#include <shared_mutex>
#include <thread>
#include <vector>
#include <unordered_map>

class ConfigurationManager {
public:
    // Потокобезпечне читання (Shared / Reader)
    std::string get_option(const std::string& key) const {
        std::shared_lock<std::shared_mutex> lock(mutex_);
        auto it = config_db_.find(key);
        return (it != config_db_.end()) ? it->second : "";
    }

    // Потокобезпечний запис (Exclusive / Writer)
    void set_option(const std::string& key, const std::string& value) {
        std::unique_lock<std::shared_mutex> lock(mutex_);
        config_db_[key] = value;
    }

private:
    mutable std::shared_mutex mutex_;
    std::unordered_map<std::string, std::string> config_db_;
};
