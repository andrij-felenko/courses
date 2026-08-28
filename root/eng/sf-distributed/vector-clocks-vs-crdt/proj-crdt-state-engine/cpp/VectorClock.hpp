// VectorClock.hpp
#pragma once
#include <string>
#include <string_view>
#include <unordered_map>
#include <algorithm>
#include <cstdint>

enum class ClockRelation {
    Equal,       // A == B
    Before,      // A < B (A causal ancestor of B)
    After,       // A > B (A causal descendant of B)
    Concurrent   // A || B (Conflict)
};

class VectorClock {
public:
    using NodeId = std::string;
    using Counter = uint64_t;

    [[nodiscard]] Counter get(std::string_view node_id) const noexcept {
        auto it = clock_.find(std::string(node_id));
        return it != clock_.end() ? it->second : 0;
    }

    void set(std::string_view node_id, Counter value) {
        clock_[std::string(node_id)] = value;
    }

    Counter increment(std::string_view node_id) {
        return ++clock_[std::string(node_id)];
    }

    void merge(const VectorClock& other) {
        for (const auto& [node, count] : other.clock_) {
            clock_[node] = std::max(clock_[node], count);
        }
    }

    [[nodiscard]] ClockRelation compare(const VectorClock& other) const noexcept {
        bool this_greater = false;
        bool other_greater = false;

        for (const auto& [node, count] : clock_) {
            const auto other_count = other.get(node);
            if (count > other_count) this_greater = true;
            if (count < other_count) other_greater = true;
        }

        for (const auto& [node, other_count] : other.clock_) {
            if (!clock_.contains(node)) {
                if (other_count > 0) other_greater = true;
            }
        }

        if (!this_greater && !other_greater) return ClockRelation::Equal;
        if (this_greater && !other_greater)  return ClockRelation::After;
        if (!this_greater && other_greater)  return ClockRelation::Before;
        return ClockRelation::Concurrent;
    }

    [[nodiscard]] const std::unordered_map<NodeId, Counter>& entries() const noexcept {
        return clock_;
    }

private:
    std::unordered_map<NodeId, Counter> clock_;
};
