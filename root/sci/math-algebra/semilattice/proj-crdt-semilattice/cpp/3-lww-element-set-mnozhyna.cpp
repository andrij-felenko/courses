#include <unordered_map>
#include <chrono>

struct ElementTimestamp {
    uint64_t add_time = 0;
    uint64_t remove_time = 0;
};

class LWWSet {
public:
    void add(const std::string& value, uint64_t timestamp) {
        elements_[value].add_time = std::max(elements_[value].add_time, timestamp);
    }

    void remove(const std::string& value, uint64_t timestamp) {
        elements_[value].remove_time = std::max(elements_[value].remove_time, timestamp);
    }

    [[nodiscard]] bool contains(const std::string& value) const {
        auto it = elements_.find(value);
        if (it == elements_.end()) {
            return false;
        }
        return it->second.add_time > it->second.remove_time;
    }

    // Злиття над join-напіврешіткою: покомпонентний максимум міток часу
    void merge(const LWWSet& other) {
        for (const auto& [val, ts] : other.elements_) {
            elements_[val].add_time = std::max(elements_[val].add_time, ts.add_time);
            elements_[val].remove_time = std::max(elements_[val].remove_time, ts.remove_time);
        }
    }

private:
    std::unordered_map<std::string, ElementTimestamp> elements_;
};
