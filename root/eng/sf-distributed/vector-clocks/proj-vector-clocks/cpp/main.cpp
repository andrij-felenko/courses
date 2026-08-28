#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <algorithm>
#include <optional>

enum class CausalOrder {
    Equal,
    Before,
    After,
    Concurrent
};

class VectorClock {
public:
    explicit VectorClock(size_t size = 0) : counters_(size, 0) {}

    void tick(size_t node_id) {
        if (node_id < counters_.size()) {
            counters_[node_id]++;
        }
    }

    void merge(const VectorClock& other) {
        const size_t limit = std::min(counters_.size(), other.counters_.size());
        for (size_t i = 0; i < limit; ++i) {
            counters_[i] = std::max(counters_[i], other.counters_[i]);
        }
    }

    [[nodiscard]] CausalOrder compare(const VectorClock& other) const {
        bool has_less = false;
        bool has_greater = false;
        const size_t limit = std::min(counters_.size(), other.counters_.size());

        for (size_t i = 0; i < limit; ++i) {
            if (counters_[i] < other.counters_[i]) {
                has_less = true;
            } else if (counters_[i] > other.counters_[i]) {
                has_greater = true;
            }
        }

        if (!has_less && !has_greater) return CausalOrder::Equal;
        if (has_less && !has_greater)  return CausalOrder::Before;
        if (!has_less && has_greater)  return CausalOrder::After;
        return CausalOrder::Concurrent;
    }

    [[nodiscard]] uint32_t get(size_t node_id) const {
        return node_id < counters_.size() ? counters_[node_id] : 0;
    }

    void set(size_t node_id, uint32_t val) {
        if (node_id < counters_.size()) {
            counters_[node_id] = val;
        }
    }

    [[nodiscard]] size_t size() const noexcept { return counters_.size(); }

    void print() const {
        std::cout << "[";
        for (size_t i = 0; i < counters_.size(); ++i) {
            std::cout << counters_[i] << (i + 1 < counters_.size() ? ", " : "");
        }
        std::cout << "]";
    }

private:
    std::vector<uint32_t> counters_;
};

struct Message {
    size_t sender_id;
    VectorClock clock;
    std::string payload;
};

class Node {
public:
    Node(size_t node_id, size_t cluster_size)
        : node_id_(node_id), clock_(cluster_size) {}

    void receive_message(size_t sender_id, const VectorClock& msg_clock, std::string_view payload) {
        if (can_deliver(sender_id, msg_clock)) {
            deliver(sender_id, msg_clock, payload);
        } else {
            buffer_.push_back(Message{sender_id, msg_clock, std::string(payload)});
            std::cout << "[Вузол " << node_id_ << "] Затримано в буфері від Вузла "
                      << sender_id << ": \"" << payload << "\"\n";
        }
    }

    [[nodiscard]] const VectorClock& clock() const noexcept { return clock_; }

private:
    [[nodiscard]] bool can_deliver(size_t sender_id, const VectorClock& msg_clock) const {
        if (msg_clock.get(sender_id) != clock_.get(sender_id) + 1) {
            return false;
        }
        for (size_t i = 0; i < clock_.size(); ++i) {
            if (i != sender_id && msg_clock.get(i) > clock_.get(i)) {
                return false;
            }
        }
        return true;
    }

    void deliver(size_t sender_id, const VectorClock& msg_clock, std::string_view payload) {
        clock_.set(sender_id, msg_clock.get(sender_id));
        std::cout << "[Вузол " << node_id_ << "] Доставлено від Вузла " << sender_id
                  << ": \"" << payload << "\" (Вектор: ";
        clock_.print();
        std::cout << ")\n";

        bool progress = true;
        while (progress) {
            progress = false;
            for (auto it = buffer_.begin(); it != buffer_.end(); ++it) {
                if (can_deliver(it->sender_id, it->clock)) {
                    Message ready_msg = std::move(*it);
                    buffer_.erase(it);
                    clock_.set(ready_msg.sender_id, ready_msg.clock.get(ready_msg.sender_id));
                    std::cout << "[Вузол " << node_id_ << "] Розблоковано з буфера від Вузла "
                              << ready_msg.sender_id << ": \"" << ready_msg.payload << "\"\n";
                    progress = true;
                    break;
                }
            }
        }
    }

    size_t node_id_;
    VectorClock clock_;
    std::vector<Message> buffer_;
};
