// C++20 узагальнена шаблонна структура
#include <vector>
#include <memory>
#include <optional>
#include <functional>
#include <cstdint>
#include <array>

template <typename Key, typename Value, typename Compare = std::less<Key>>
class SkipList {
public:
    static constexpr size_t kMaxLevel = 32;
    static constexpr double kBranchingProb = 0.25;

    enum class Status {
        kOk = 0,
        kNotFound = -1,
        kAlreadyExists = -2,
        kOutOfMemory = -3,
        kInvalidArgument = -4
    };

    struct Stats {
        size_t total_nodes{0};
        size_t current_max_level{1};
        size_t total_memory_bytes{0};
        double avg_pointers_per_node{0.0};
        std::array<size_t, kMaxLevel> level_counts{};
    };

private:
    struct Node {
        Key key;
        Value value;
        std::vector<Node*> forward;

        Node(const Key& k, const Value& v, size_t level)
            : key(k), value(v), forward(level, nullptr) {}

        explicit Node(size_t level)
            : key{}, value{}, forward(level, nullptr) {}
    };

    size_t current_level_{1};
    size_t element_count_{0};
    std::unique_ptr<Node> head_;
    Compare comp_{};
};
