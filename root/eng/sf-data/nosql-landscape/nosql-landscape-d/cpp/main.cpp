#include <iostream>
#include <string>
#include <unordered_map>
#include <optional>

class SimpleKVStore {
public:
    void put(const std::string& key, const std::string& value) {
        table_[key] = value;
        std::cout << "[LOG C++] PUT ключ: " << key << " => " << value << "\n";
    }

    std::optional<std::string> get(const std::string& key) const {
        auto it = table_.find(key);
        if (it != table_.end()) {
            return it->second;
        }
        return std::nullopt;
    }

    void remove(const std::string& key) {
        table_.erase(key);
        std::cout << "[LOG C++] DELETE ключ: " << key << "\n";
    }

private:
    std::unordered_map<std::string, std::string> table_;
};
