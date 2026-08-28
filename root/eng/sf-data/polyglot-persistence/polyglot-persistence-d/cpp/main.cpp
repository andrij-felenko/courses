#include <iostream>
#include <string>
#include <unordered_map>
#include <vector>

class PolyglotStore {
public:
    void commit_order(int id, const std::string& data) {
        // 1. Атомарний запис у primary store
        primary_store_[id] = data;
        outbox_queue_.push_back({id, data});
    }

    void process_sync() {
        for (const auto& [id, payload] : outbox_queue_) {
            // 2. Ідемпотентне оновлення кешу та пошукового індексу
            read_cache_[id] = payload;
        }
        outbox_queue_.clear();
    }

    std::string fast_read(int id) const {
        auto it = read_cache_.find(id);
        if (it != read_cache_.end()) return it->second;
        return "";
    }

private:
    std::unordered_map<int, std::string> primary_store_;
    std::vector<std::pair<int, std::string>> outbox_queue_;
    std::unordered_map<int, std::string> read_cache_;
};
