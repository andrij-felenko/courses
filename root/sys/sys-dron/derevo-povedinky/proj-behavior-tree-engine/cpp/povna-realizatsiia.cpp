#include <cstdint>
#include <string_view>
#include <span>
#include <array>
#include <variant>
#include <optional>
#include <concepts>

namespace autopilot::bt {

enum class NodeStatus : uint8_t {
    Idle = 0,
    Running,
    Success,
    Failure
};

enum class NodeType : uint8_t {
    Action,
    Condition,
    Sequence,
    ReactiveSequence,
    Fallback,
    ReactiveFallback,
    ParallelMOfN,
    Inverter,
    Timeout
};

constexpr size_t MaxNodes = 32;
constexpr size_t MaxChildren = 8;
constexpr size_t MaxBlackboardEntries = 16;

using BlackboardValue = std::variant<bool, int32_t, float>;

struct BlackboardEntry {
    std::string_view key{};
    BlackboardValue value{};
    bool is_set{false};
};

class Blackboard {
public:
    template <typename T>
    bool set(std::string_view key, T val) noexcept {
        for (auto& entry : entries_) {
            if (entry.is_set && entry.key == key) {
                entry.value = val;
                return true;
            }
        }
        if (count_ >= MaxBlackboardEntries) return false;
        entries_[count_] = BlackboardEntry{key, val, true};
        count_++;
        return true;
    }

    template <typename T>
    [[nodiscard]] std::optional<T> get(std::string_view key) const noexcept {
        for (size_t i = 0; i < count_; ++i) {
            if (entries_[i].is_set && entries_[i].key == key) {
                if (const auto* val = std::get_if<T>(&entries_[i].value)) {
                    return *val;
                }
            }
        }
        return std::nullopt;
    }

    void clear() noexcept {
        count_ = 0;
        for (auto& entry : entries_) {
            entry.is_set = false;
        }
    }

private:
    std::array<BlackboardEntry, MaxBlackboardEntries> entries_{};
    size_t count_{0};
};

struct Node;
using TickFn = NodeStatus (*)(Node& self, Blackboard& bb) noexcept;
using HaltFn = void (*)(Node& self, Blackboard& bb) noexcept;

struct Node {
    uint8_t id{0};
    NodeType type{NodeType::Action};
    NodeStatus status{NodeStatus::Idle};
    TickFn tick_fn{nullptr};
    HaltFn halt_fn{nullptr};
    std::array<uint8_t, MaxChildren> children{};
    uint8_t child_count{0};
    uint8_t running_child_idx{0};
    uint8_t threshold_m{1};
    uint32_t timeout_ticks{0};
    uint32_t elapsed_ticks{0};
    void* user_data{nullptr};
};

class BehaviorTree {
public:
    BehaviorTree() noexcept = default;

    uint8_t create_node(NodeType type, TickFn tick = nullptr, HaltFn halt = nullptr) noexcept {
        if (node_count_ >= MaxNodes) return 0xFF;
        uint8_t id = node_count_++;
        nodes_[id] = Node{id, type, NodeStatus::Idle, tick, halt, {}, 0, 0, 1, 0, 0, nullptr};
        return id;
    }

    bool add_child(uint8_t parent_id, uint8_t child_id) noexcept {
        if (parent_id >= node_count_ || child_id >= node_count_) return false;
        auto& parent = nodes_[parent_id];
        if (parent.child_count >= MaxChildren) return false;
        parent.children[parent.child_count++] = child_id;
        return true;
    }

    void set_parallel_threshold(uint8_t node_id, uint8_t m) noexcept {
        if (node_id < node_count_) {
            nodes_[node_id].threshold_m = m;
        }
    }

    void set_timeout_ticks(uint8_t node_id, uint32_t ticks) noexcept {
        if (node_id < node_count_) {
            nodes_[node_id].timeout_ticks = ticks;
        }
    }

    void set_root(uint8_t root_id) noexcept {
        root_id_ = root_id;
    }

    void halt_node(uint8_t node_id) noexcept {
        if (node_id >= node_count_) return;
        auto& n = nodes_[node_id];
        if (n.status == NodeStatus::Running) {
            if (n.halt_fn) {
                n.halt_fn(n, blackboard_);
            }
            for (size_t i = 0; i < n.child_count; ++i) {
                halt_node(n.children[i]);
            }
            n.status = NodeStatus::Idle;
            n.running_child_idx = 0;
            n.elapsed_ticks = 0;
        }
    }

    NodeStatus tick_node(uint8_t node_id) noexcept {
        if (node_id >= node_count_) return NodeStatus::Failure;
        auto& n = nodes_[node_id];

        switch (n.type) {
            case NodeType::Action:
            case NodeType::Condition:
                n.status = n.tick_fn ? n.tick_fn(n, blackboard_) : NodeStatus::Failure;
                return n.status;

            case NodeType::Sequence: {
                for (size_t i = n.running_child_idx; i < n.child_count; ++i) {
                    const auto s = tick_node(n.children[i]);
                    if (s == NodeStatus::Running) {
                        n.running_child_idx = static_cast<uint8_t>(i);
                        n.status = NodeStatus::Running;
                        return NodeStatus::Running;
                    }
                    if (s == NodeStatus::Failure) {
                        n.running_child_idx = 0;
                        n.status = NodeStatus::Failure;
                        return NodeStatus::Failure;
                    }
                }
                n.running_child_idx = 0;
                n.status = NodeStatus::Success;
                return NodeStatus::Success;
            }

            case NodeType::ReactiveSequence: {
                for (size_t i = 0; i < n.child_count; ++i) {
                    const auto s = tick_node(n.children[i]);
                    if (s == NodeStatus::Failure) {
                        if (n.status == NodeStatus::Running && n.running_child_idx > i) {
                            halt_node(n.children[n.running_child_idx]);
                        }
                        n.running_child_idx = 0;
                        n.status = NodeStatus::Failure;
                        return NodeStatus::Failure;
                    }
                    if (s == NodeStatus::Running) {
                        if (n.status == NodeStatus::Running && n.running_child_idx != i) {
                            halt_node(n.children[n.running_child_idx]);
                        }
                        n.running_child_idx = static_cast<uint8_t>(i);
                        n.status = NodeStatus::Running;
                        return NodeStatus::Running;
                    }
                }
                n.running_child_idx = 0;
                n.status = NodeStatus::Success;
                return NodeStatus::Success;
            }

            case NodeType::Fallback: {
                for (size_t i = n.running_child_idx; i < n.child_count; ++i) {
                    const auto s = tick_node(n.children[i]);
                    if (s == NodeStatus::Running) {
                        n.running_child_idx = static_cast<uint8_t>(i);
                        n.status = NodeStatus::Running;
                        return NodeStatus::Running;
                    }
                    if (s == NodeStatus::Success) {
                        n.running_child_idx = 0;
                        n.status = NodeStatus::Success;
                        return NodeStatus::Success;
                    }
                }
                n.running_child_idx = 0;
                n.status = NodeStatus::Failure;
                return NodeStatus::Failure;
            }

            case NodeType::ReactiveFallback: {
                for (size_t i = 0; i < n.child_count; ++i) {
                    const auto s = tick_node(n.children[i]);

                    if (s == NodeStatus::Running) {
                        if (n.status == NodeStatus::Running && n.running_child_idx > i) {
                            halt_node(n.children[n.running_child_idx]);
                        }
                        n.running_child_idx = static_cast<uint8_t>(i);
                        n.status = NodeStatus::Running;
                        return NodeStatus::Running;
                    }
                    if (s == NodeStatus::Success) {
                        if (n.status == NodeStatus::Running && n.running_child_idx != i) {
                            halt_node(n.children[n.running_child_idx]);
                        }
                        n.running_child_idx = 0;
                        n.status = NodeStatus::Success;
                        return NodeStatus::Success;
                    }
                }
                n.running_child_idx = 0;
                n.status = NodeStatus::Failure;
                return NodeStatus::Failure;
            }

            case NodeType::ParallelMOfN: {
                uint8_t success_cnt = 0;
                uint8_t failure_cnt = 0;

                for (size_t i = 0; i < n.child_count; ++i) {
                    const auto s = tick_node(n.children[i]);
                    if (s == NodeStatus::Success) success_cnt++;
                    else if (s == NodeStatus::Failure) failure_cnt++;
                }

                if (success_cnt >= n.threshold_m) {
                    for (size_t i = 0; i < n.child_count; ++i) {
                        halt_node(n.children[i]);
                    }
                    n.status = NodeStatus::Success;
                    return NodeStatus::Success;
                }

                if (failure_cnt > (n.child_count - n.threshold_m)) {
                    for (size_t i = 0; i < n.child_count; ++i) {
                        halt_node(n.children[i]);
                    }
                    n.status = NodeStatus::Failure;
                    return NodeStatus::Failure;
                }

                n.status = NodeStatus::Running;
                return NodeStatus::Running;
            }

            case NodeType::Inverter: {
                if (n.child_count == 0) return NodeStatus::Failure;
                const auto s = tick_node(n.children[0]);
                if (s == NodeStatus::Success) n.status = NodeStatus::Failure;
                else if (s == NodeStatus::Failure) n.status = NodeStatus::Success;
                else n.status = s;
                return n.status;
            }

            case NodeType::Timeout: {
                if (n.child_count == 0) return NodeStatus::Failure;
                n.elapsed_ticks++;
                if (n.timeout_ticks > 0 && n.elapsed_ticks > n.timeout_ticks) {
                    halt_node(n.children[0]);
                    n.elapsed_ticks = 0;
                    n.status = NodeStatus::Failure;
                    return NodeStatus::Failure;
                }
                const auto s = tick_node(n.children[0]);
                if (s != NodeStatus::Running) {
                    n.elapsed_ticks = 0;
                }
                n.status = s;
                return s;
            }
        }
        return NodeStatus::Failure;
    }

    [[nodiscard]] NodeStatus tick() noexcept {
        return tick_node(root_id_);
    }

    Blackboard& blackboard() noexcept { return blackboard_; }
    [[nodiscard]] const Blackboard& blackboard() const noexcept { return blackboard_; }

private:
    std::array<Node, MaxNodes> nodes_{};
    uint8_t node_count_{0};
    uint8_t root_id_{0};
    Blackboard blackboard_{};
};

} // namespace autopilot::bt
