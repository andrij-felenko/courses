#include <iostream>
#include <string>
#include <unordered_map>
#include <numeric>
#include <algorithm>
#include <cstdint>
#include <vector>

class GCounter {
public:
    explicit GCounter(std::string node_id) : node_id_(std::move(node_id)) {}

    void increment(uint64_t delta = 1) {
        state_[node_id_] += delta;
    }

    [[nodiscard]] uint64_t value() const noexcept {
        uint64_t total = 0;
        for (const auto& [id, count] : state_) {
            total += count;
        }
        return total;
    }

    // Операція злиття над join-напіврешіткою: покомпонентний максимум
    void merge(const GCounter& other) {
        for (const auto& [id, count] : other.state_) {
            state_[id] = std::max(state_[id], count);
        }
    }

    [[nodiscard]] const std::unordered_map<std::string, uint64_t>& state() const noexcept {
        return state_;
    }

private:
    std::string node_id_;
    std::unordered_map<std::string, uint64_t> state_;
};
